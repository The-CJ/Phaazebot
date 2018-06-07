import re

def get_navbar(active=''):
    root = open('_WEB_/content/_navbar/navbar_content.html', 'r').read()
    navbar = root
    if active != '':
        try:
            addition = open(f'_WEB_/content/_navbar/navbar_content_{active}.html', 'r').read()
            navbar = navbar + addition
        except:
            pass

        ac = re.finditer('\\{selected_(.+)\\}', navbar)
        for c in ac:
            if c.group(0) == active:
                navbar = navbar.replace(c.group(0), 'active')
            else:
                navbar = navbar.replace(c.group(0), '')

    return navbar


def format_html_functions(self, html_string, **values):
    """
    This function will take all
    |>>>func()<<<|
    in the .html,
    execute them and insert the return vaule as string.

    returns formated html
    """
    search_results = re.finditer(self.format_html_regex, html_string)
    for hit in search_results:
        try:
            calc_ = eval(hit.group(1))
            html_string = html_string.replace(hit.group(0), calc_)
        except:
            html_string = html_string.replace(hit.group(0), '')

    return html_string


def get_login_btn(BASE, **kwargs):
    if kwargs.get('platform', None) != None:
        pass

    if kwargs.get('user', None) == None:
        no_login = open('_WEB_/content/_buttons/no_login.html', 'r').read()
        return no_login
    else:
        main_btn = open('_WEB_/content/_buttons/phaaze_login.html', 'r').read()
        main_btn = main_btn.replace('{name}', kwargs.get('user', {}).get('phaaze_username', '[NAME N/A]'))
        main_btn = main_btn.replace('{type}', kwargs.get('user', {}).get('type', '[TYPE N/A]'))
        if kwargs.get('user', {}).get('img_path', None) != None:
            img = 'HELLO'
        else:
            img = 'hidden'
        main_btn = main_btn.replace('{img_path}', img)
        return main_btn
