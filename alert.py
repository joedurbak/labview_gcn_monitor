from xmltodict import parse
from gcnmonitor import xml_tag_loader
from settings import OUTPUT_HTML_DIR
from os import listdir
from os.path import join


def get_alert_message(html_filename):
    html_dict = parse(open(html_filename, 'r').read().replace('&', ''))
    html_body_divs = xml_tag_loader(html_dict, ('html', 'body', 'div'))
    for div in html_body_divs:
        if xml_tag_loader(div, ('@id', )) == 'main_alert':
            alert_message = ""
            for div_h4 in xml_tag_loader(div, ('h4', )):
                alert_message += xml_tag_loader(div_h4, ('#text', )) + '\n'
            return alert_message


def get_new_alerts():
    old_html_filename = join(OUTPUT_HTML_DIR, 'old_html.txt')
    try:
        old_html_files = open(old_html_filename, 'r').read().split()
    except FileNotFoundError:
        old_html_files = []
    logger = open(old_html_filename, 'a+')
    for file in listdir(OUTPUT_HTML_DIR):
        if file.endswith('.html'):
            if file not in old_html_files:
                print(file)
                print("Target of Opportunity!\n" + get_alert_message(join(OUTPUT_HTML_DIR, file))+"\n")
                logger.write(file + '\n')
    logger.close()


get_new_alerts()
