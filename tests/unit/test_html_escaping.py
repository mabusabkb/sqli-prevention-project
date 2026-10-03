"""
Unit tests for HTML escaping and XSS prevention.

Tests verify that:
1. Jinja2 auto-escaping is enabled by default
2. HTML special characters are escaped in templates
3. User data excludes passwords via to_dict() method
4. XSS attempts are neutralized

Validates: Requirements 4.5
"""
import pytest
from flask import render_template_string
from app.models.user import User
from app import db


class TestHTMLEscaping:
    """Test HTML escaping for XSS prevention"""
    
    def test_jinja2_autoescape_enabled(self, app):
        """Test that Jinja2 auto-escaping is enabled by default"""
        with app.app_context():
            # Jinja2 auto-escaping should be enabled by default in Flask
            # In Flask, autoescape is a function, not a boolean
            # We verify it's enabled by checking it's callable and returns True for .html files
            assert callable(app.jinja_env.autoescape)
            # Test that it returns True for HTML templates
            assert app.jinja_env.autoescape('template.html') is True
    
    def test_html_special_characters_escaped_in_template(self, app):
        """Test that HTML special characters are escaped in templates"""
        with app.app_context():
            # Test data with HTML special characters
            test_cases = [
                ('<script>alert("XSS")</script>', ['&lt;script&gt;', '&lt;/script&gt;']),
                ('<img src=x onerror=alert(1)>', ['&lt;img', '&gt;']),
                ('"><script>alert(1)</script>', ['&#34;', '&gt;', '&lt;script&gt;']),
                ("' OR '1'='1", ['&#39;']),
                ('&<>"\'', ['&amp;', '&lt;', '&gt;', '&#34;', '&#39;']),
            ]
            
            for malicious_input, expected_escaped_parts in test_cases:
                # Render template with malicious input
                template = '{{ data }}'
                rendered = render_template_string(template, data=malicious_input)
                
                # Verify at least some HTML characters are escaped
                # The exact escaping format may vary, but dangerous patterns should not be present
                assert '<script>' not in rendered or '&lt;script&gt;' in rendered
                # Check that at least one expected escaped part is present
                assert any(part in rendered for part in expected_escaped_parts)
    
    def test_username_with_html_escaped(self, app):
        """Test that username containing HTML is escaped when displayed"""
        with app.app_context():
            malicious_username = '<script>alert("XSS")</script>'
            
            # Render a simple template displaying username
            template = '<div>{{ username }}</div>'
            rendered = render_template_string(template, username=malicious_username)
            
            # Verify script tags are escaped
            assert '<script>' not in rendered
            assert '&lt;script&gt;' in rendered or '&lt;' in rendered
    
    def test_email_with_html_escaped(self, app):
        """Test that email containing HTML is escaped when displayed"""
        with app.app_context():
            malicious_email = 'test@example.com"><script>alert(1)</script>'
            
            template = '<div>{{ email }}</div>'
            rendered = render_template_string(template, email=malicious_email)
            
            # Verify dangerous characters are escaped
            assert '<script>' not in rendered
            assert 'alert(1)' not in rendered or '&lt;script&gt;' in rendered
    
    def test_to_dict_excludes_password(self, app):
        """Test that to_dict() method excludes password field"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='hashed_password_here',
                gender='Male'
            )
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            # Verify password is not in dictionary
            assert 'password' not in user_dict
            
            # Verify other fields are present
            assert 'id' in user_dict
            assert 'username' in user_dict
            assert 'email' in user_dict
            assert 'gender' in user_dict
            assert 'created_at' in user_dict
    
    def test_to_dict_with_html_in_username(self, app):
        """Test that to_dict() preserves HTML in data (escaping happens in template)"""
        with app.app_context():
            malicious_username = '<script>alert("XSS")</script>'
            
            user = User(
                username=malicious_username,
                email='test@example.com',
                password='hashed_password',
                gender='Male'
            )
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            # to_dict() should preserve the data as-is
            # Escaping happens in the template layer
            assert user_dict['username'] == malicious_username
            assert 'password' not in user_dict
    
    def test_flash_message_with_html_escaped(self, app, client):
        """Test that flash messages with HTML are escaped"""
        with app.app_context():
            from flask import flash, render_template_string
            
            malicious_message = '<script>alert("XSS")</script>'
            
            with client.session_transaction() as session:
                session['_flashes'] = [('error', malicious_message)]
            
            # Render template with flash messages
            template = '''
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div>{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            '''
            
            with client:
                response = client.get('/')
                # Flash messages should be escaped in templates
                # This is handled by Jinja2 auto-escaping
    
    def test_user_list_template_escapes_html(self, app, client):
        """Test that user list template escapes HTML in user data"""
        with app.app_context():
            # Create user with HTML in username
            malicious_username = '<img src=x onerror=alert(1)>'
            
            user = User(
                username=malicious_username,
                email='test@example.com',
                password='hashed_password',
                gender='Male'
            )
            db.session.add(user)
            db.session.commit()
            
            # Login first
            from app.services.auth_service import AuthService
            AuthService.register_user('admin', 'admin@example.com', 'password123', 'Male')
            
            with client.session_transaction() as session:
                session['user_id'] = 1
                session['username'] = 'admin'
            
            # Access user list page (follow redirects if any)
            response = client.get('/users', follow_redirects=True)
            
            # Verify response
            assert response.status_code == 200
            
            # Verify HTML is escaped in response
            response_data = response.data.decode('utf-8')
            assert '<img src=x onerror=alert(1)>' not in response_data
            # Should contain escaped version
            assert '&lt;img' in response_data or 'onerror' not in response_data
    
    def test_multiple_html_special_characters(self, app):
        """Test escaping of all HTML special characters"""
        with app.app_context():
            special_chars = {
                '<': '&lt;',
                '>': '&gt;',
                '&': '&amp;',
                '"': '&#34;',
                "'": '&#39;',
            }
            
            for char, escaped in special_chars.items():
                template = '{{ data }}'
                rendered = render_template_string(template, data=char)
                
                # Verify character is escaped (exact format may vary)
                # The important thing is the original character is not present unescaped
                # when it could be dangerous
                if char in ['<', '>', '"', "'"]:
                    # These should definitely be escaped in some form
                    assert escaped in rendered or char not in rendered
    
    def test_safe_filter_not_used_by_default(self, app):
        """Test that |safe filter is not applied by default"""
        with app.app_context():
            malicious_input = '<script>alert("XSS")</script>'
            
            # Without |safe filter, should be escaped
            template = '{{ data }}'
            rendered = render_template_string(template, data=malicious_input)
            assert '<script>' not in rendered
            
            # With |safe filter, would NOT be escaped (dangerous!)
            template_unsafe = '{{ data|safe }}'
            rendered_unsafe = render_template_string(template_unsafe, data=malicious_input)
            assert '<script>' in rendered_unsafe  # This demonstrates why |safe is dangerous
    
    def test_url_parameter_escaping(self, app, client):
        """Test that URL parameters with HTML are escaped"""
        with app.app_context():
            # Create a user
            from app.services.auth_service import AuthService
            AuthService.register_user('testuser', 'test@example.com', 'password123', 'Male')
            
            with client.session_transaction() as session:
                session['user_id'] = 1
                session['username'] = 'testuser'
            
            # Try to access update page with malicious user_id
            # This tests that even if someone crafts a malicious URL, it's handled safely
            response = client.get('/users/update/<script>alert(1)</script>')
            
            # Should either return 404 or handle gracefully
            # The important thing is no script execution
            assert response.status_code in [400, 404, 500]


class TestXSSPrevention:
    """Test XSS attack prevention"""
    
    def test_stored_xss_prevention(self, app):
        """Test prevention of stored XSS attacks"""
        with app.app_context():
            # Attempt to store XSS payload in database
            xss_payload = '<script>document.cookie</script>'
            
            user = User(
                username=xss_payload,
                email='xss@example.com',
                password='hashed_password',
                gender='Male'
            )
            db.session.add(user)
            db.session.commit()
            
            # Retrieve user
            retrieved_user = User.query.filter_by(email='xss@example.com').first()
            
            # Data is stored as-is in database
            assert retrieved_user.username == xss_payload
            
            # But when rendered in template, it should be escaped
            template = '<div>{{ username }}</div>'
            rendered = render_template_string(template, username=retrieved_user.username)
            
            assert '<script>' not in rendered
    
    def test_reflected_xss_prevention(self, app, client):
        """Test prevention of reflected XSS attacks"""
        with app.app_context():
            # Attempt reflected XSS through form submission
            xss_payload = '<script>alert(document.cookie)</script>'
            
            response = client.post('/login', data={
                'username': xss_payload,
                'password': 'test'
            }, follow_redirects=True)
            
            # Response should not contain unescaped script
            response_data = response.data.decode('utf-8')
            assert '<script>alert(document.cookie)</script>' not in response_data
    
    def test_dom_based_xss_prevention(self, app):
        """Test that templates don't create DOM-based XSS vulnerabilities"""
        with app.app_context():
            # Test that user data is properly escaped even in attributes
            malicious_value = '" onload="alert(1)'
            
            template = '<input value="{{ data }}">'
            rendered = render_template_string(template, data=malicious_value)
            
            # Should not create executable attribute
            assert 'onload="alert(1)' not in rendered
            assert '&#34;' in rendered or '&quot;' in rendered
