from xmltodict import parse
from gcnmonitor import xml_tag_loader
from settings import OUTPUT_HTML_DIR, INCLUDE_ALERT_MESSAGES
from os import listdir
from os.path import join


def get_notice_type(file_string):
    split_string = file_string.split('.')
    file_string = ''.join(split_string[:len(split_string)-2])
    split_string = file_string.split('_')
    return int(split_string[len(split_string)-1])


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
                if get_notice_type(file) in INCLUDE_ALERT_MESSAGES:
                    print("Target of Opportunity!\n" + get_alert_message(join(OUTPUT_HTML_DIR, file))+"\n")
                    print(file)
                else:
                    print('Ignore')
                logger.write(file + '\n')
    logger.close()


get_new_alerts()
