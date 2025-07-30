import re


def read_file(path):
    with open(path, 'r', encoding="utf-8") as fp:
        content = fp.read()
        return content
        
def read_conf():
#     return """<VirtualHost *:80>
#         # The ServerName directive sets the request scheme, hostname and port that
#         # the server uses to identify itself. This is used when creating
#         # redirection URLs. In the context of virtual hosts, the ServerName
#         # specifies what hostname must appear in the request's Host: header to
#         # match this virtual host. For the default virtual host (this file) this
#         # value is not decisive as it is used as a last resort host regardless.
#         # However, you must set it for any further virtual host explicitly.
#         #ServerName www.example.com

#         ServerAdmin webmaster@localhost
#         DocumentRoot /var/www/html

#         # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
#         # error, crit, alert, emerg.
#         # It is also possible to configure the loglevel for particular
#         # modules, e.g.
#         #LogLevel info ssl:warn

#         ErrorLog ${APACHE_LOG_DIR}/error.log
#         CustomLog ${APACHE_LOG_DIR}/access.log combined

#         # For most configuration files from conf-available/, which are
#         # enabled or disabled at a global level, it is possible to
#         # include a line for only one particular virtual host. For example the
#         # following line enables the CGI configuration for this host only
#         # after it has been globally disabled with "a2disconf".
#         #Include conf-available/serve-cgi-bin.conf
# </VirtualHost>"""
    return read_file("/etc/apache2/sites-available/000-default.conf")

def clean_conf(apache_conf, root_path):
    apache_conf = re.sub(r'\n\s.*ProxyPass\s+' + re.escape(root_path) + r'\s+.*\n', '\n', apache_conf)
    apache_conf = re.sub(r'ProxyPass\s+' + re.escape(root_path) + r'\s+.*\n', '', apache_conf)
    apache_conf = re.sub(r'\n\s.*ProxyPassReverse\s+' + re.escape(root_path) + r'\s+.*\n', '\n', apache_conf)
    apache_conf = re.sub(r'ProxyPassReverse\s+' + re.escape(root_path) + r'\s+.*\n', '', apache_conf)
    # return apache_conf
    return re.sub(r'[ \t]+</VirtualHost>', '</VirtualHost>', apache_conf)

def collapse_empty_lines(conf: str) -> str:
    # Replace multiple consecutive newlines (with optional whitespace) with a single newline
    return re.sub(r'\n\s*\n+', '\n\n', conf.strip()) + '\n'

def sub_at_start(apache_conf, root_path, api_target):
    return re.sub(
            r'(<VirtualHost\b.*?>)', 
            f'\\1\n    ProxyPass {root_path} {api_target}\n    ProxyPassReverse {root_path} {api_target}', 
            apache_conf, 
            count=1
        )

def sub_at_end(apache_conf, root_path, api_target):
    return re.sub(r'</VirtualHost>', f'    ProxyPass {root_path} {api_target}\n    ProxyPassReverse {root_path} {api_target}\n</VirtualHost>', apache_conf)

replace_conf = """# The ServerName directive sets the request scheme, hostname and port that
""".strip()

def make_apache_content(apache_conf, root_path, api_target):

    # Remove replace_conf content
    apache_conf = apache_conf.replace(replace_conf, "")
      

    # Remove existing ProxyPass and ProxyPassReverse directives for the root_path
    apache_conf = clean_conf(apache_conf, root_path)

    # Add new ProxyPass and ProxyPassReverse directives based on the root_path
    if root_path == "/":
        return collapse_empty_lines(sub_at_end(apache_conf, root_path, api_target))
    else:
        # Add new directives right after the VirtualHost opening tag
        return collapse_empty_lines(sub_at_start(apache_conf, root_path, api_target))

# python -m src.bota.apache_utils
if __name__ == "__main__":
    apache_conf = read_conf().strip()
    print(replace_conf in apache_conf)
    # print("before",apache_conf)
    
    # print("after",apache_conf.replace(replace_conf, ""))