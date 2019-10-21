from gcnmonitor import (
    HTMLOutput, GCNProcessor, archived_xml_dir, html_templates_dict, template_html_dir, output_html_dir, list_plus
)
import os
from six.moves.urllib.parse import quote_plus
from collections import OrderedDict


class RootTester:
    def __init__(self, ivorn_name):
        self.ivorn_name = ivorn_name
        self.attrib = {
            'ivorn': "test_{0}".format(quote_plus(self.ivorn_name)),
        }


def test_gcn_processor_init(filename, archive_dir, output_dir, template_dir, html_templates_dictionary, root):
    with open(filename, 'r') as file:
        xml_string = file.read()
    print(filename)
    gcn_process_dict = {
        'incoming_xml': xml_string,
        'archive_dir': archive_dir,
        'output_dir': output_dir,
        'template_dir': template_dir,
        'html_templates_dictionary': html_templates_dictionary,
        'root': root,
    }
    gcn_processor = GCNProcessor(**gcn_process_dict)
    print("GCN PROCESSOR INITIALIZATION TEST PASSED")
    return gcn_processor


def test_gcn_processor_archive(gcn_processor_object):
    archived_xml_file = gcn_processor_object.archive_xml()
    with open(archived_xml_file, 'r') as file:
        xml_str = file.read()
    if len(xml_str) > 0:
        print("GCN PROCESSOR ARCHIVE TEST PASSED")
        return archived_xml_file
    else:
        raise ValueError("Empty XML archive file!")


def test_html_output_init(incoming_xml, html_templates):
    html_handler = HTMLOutput(incoming_xml, **html_templates)
    print("HTML OUTPUT INITIALIZATION TEST PASSED")
    return html_handler


def test_gcn_processor_save_output_html(gcn_object, html_object, archived_xml_filename):
    gcn_object.save_output_html(html_object.html_out(), archived_xml_filename)
    print("GCN PROCESSOR SAVE HTML TEST PASSED")


def test_list_plus():
    test_dict = {'a': 1, 'b': 2}
    test_ordered_dict = OrderedDict([('a', 1), ('b', 2)])
    test_list = [{'a': 1, 'b': 2}, {'c': 1, 'd': 2}]
    test_tuple = ({'a': 1, 'b': 2}, {'c': 1, 'd': 2})
    test_string = 'a'
    test_int = 5
    if [test_dict] == list_plus(test_dict):
        print("LIST PLUS TEST DICT: PASSED")
    else:
        print("LIST PLUS TEST DICT: FAIL")
    if [test_ordered_dict] == list_plus(test_ordered_dict):
        print("LIST PLUS TEST ORDERED DICT: PASSED")
    else:
        print("LIST PLUS TEST ORDERED DICT: FAIL")
    if test_list == list_plus(test_list):
        print("LIST PLUS TEST LIST: PASSED")
    else:
        print("LIST PLUS TEST LIST: FAIL")
    if test_tuple == list_plus(test_tuple):
        print("LIST PLUS TEST TUPLE: PASSED")
    else:
        print("LIST PLUS TEST TUPLE: FAIL")
    if [] == list_plus(test_string):
        print("LIST PLUS TEST STRING: PASSED")
    else:
        print("LIST PLUS TEST STRING: FAIL")
    if [] == list_plus(test_int):
        print("LIST PLUS TEST INT: PASSED")
    else:
        print("LIST PLUS TEST INT: FAIL")


def test_all_xml_to_html():
    for xml_filename in os.listdir(archived_xml_dir):
        if xml_filename.endswith(".xml"):
            gcn_obj = test_gcn_processor_init(
                os.path.join(archived_xml_dir, xml_filename),
                archived_xml_dir, output_html_dir, template_html_dir, html_templates_dict,
                RootTester(xml_filename.replace(".xml", ""))
            )
            gcn_obj.gcn_processor()


# xml_file = os.path.join(archived_xml_dir, os.listdir(archived_xml_dir)[0])
# gcn_obj = test_gcn_processor_init(
#     xml_file, archived_xml_dir, output_html_dir, template_html_dir, html_templates_dict, RootTester
# )
# archive_file = test_gcn_processor_archive(gcn_obj)
# html_obj = test_html_output_init(gcn_obj.incoming_xml, html_templates_dict)
# test_gcn_processor_save_output_html(gcn_obj, html_obj, archive_file)
# test_list_plus()
# print(html_obj.load_header())
# print("xml_file: {0}".format(xml_file))
# print("archive_file: {0}".format(archive_file))
# print("********************* load_body_title_who ***********************")
# print(html_obj.load_body_title_who())
# print("********************* load_body_title_what_param ***********************")
# print(html_obj.load_body_title_what_param())
# print("********************* load_body_title_what_table_to_group ***********************")
# print(html_obj.load_body_title_what_table_to_group())
# print("********************* load_body_title_what_group ***********************")
# print(html_obj.load_body_title_what_group())
# print("********************* load_body_what_table ***********************")
# print(html_obj.load_body_what_table())
# print("********************* load_body_title_whenwhere ***********************")
# print(html_obj.load_body_title_whenwhere())
test_all_xml_to_html()
