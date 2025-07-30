import xml.etree.ElementTree as ET
import os
from typing import List, Tuple

def strip_namespace(tag: str) -> str:
    """Remove namespace from XML tag."""
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag

def compute_xpath_strip(xpath: str) -> str:
    """
    Return the XPath starting at /AppHdr or /Document, or just ensure it starts with '/'.
    """
    # Look for '/AppHdr' or '/Document' anywhere in the XPath
    idx_apphdr = xpath.find('/AppHdr')
    idx_document = xpath.find('/Document')
    if idx_apphdr != -1:
        return xpath[idx_apphdr:]
    elif idx_document != -1:
        return xpath[idx_document:]
    else:
        return '' # xpath #'/' + xpath.lstrip('/')

def get_xpath_and_value(element: ET.Element, path: str = '', strip_space: bool = True) -> List[tuple]:
    """
    Recursively generate (XPath, XPath_strip, value) tuples for all elements in the XML tree, stripping namespaces for clarity.
    Returns: List of (xpath, xpath_strip, value) tuples
    """
    tag = strip_namespace(element.tag)
    if path:
        current_path = f"{path}/{tag}"
    else:
        current_path = tag
    value = element.text or ''
    if strip_space:
        value = value.strip()
    else:
        value = value.replace('\n', '')
    xpath_strip = compute_xpath_strip(current_path)
    results = [(current_path, xpath_strip, value)]
    for child in element:
        results.extend(get_xpath_and_value(child, current_path, strip_space=strip_space))
    return results


def extract_metadata(tree: ET.ElementTree) -> tuple:
    """
    Extract XSD (from Document tag's xmlns attribute), MsgId (from MsgId tag under Document), and AppHdr metadata.
    Returns tuple:
      (xsd, msgid, fr, to, credt, bizmsgidr, bizsvc)
    All are strings, empty if not found.
    """
    xsd = ''
    msgid = ''
    fr = ''
    to = ''
    credt = ''
    bizmsgidr = ''
    bizsvc = ''
    msgdefidr = None
    root = tree.getroot()
    AppHdr_elem = None
    document_elem = None
    for elem in root.iter():
        if strip_namespace(elem.tag) == 'AppHdr':
            AppHdr_elem = elem
            break
    for elem in root.iter():
        if strip_namespace(elem.tag) == 'Document':
            document_elem = elem
            break
    if document_elem is not None:
        # XSD from xmlns attribute (could be xmlns or xmlns:...)
        for attr in document_elem.attrib:
            if attr == 'xmlns' or 'xsd:' in document_elem.attrib[attr] or attr.startswith('{http://www.w3.org/2000/xmlns/}'):
                xsd = document_elem.attrib[attr]
                break
        # Find MsgId under Document
        for subelem in document_elem.iter():
            if strip_namespace(subelem.tag) == 'MsgId':
                msgid = (subelem.text or '').strip()
                break
    if AppHdr_elem is not None:
        # Helper to extract text from a child tag
        def get_child_text(parent, tag):
            for child in parent:
                print(child.tag)
                if strip_namespace(child.tag) == tag:
                    return child
            return None
        # Fr
        fr_elem = get_child_text(AppHdr_elem, 'Fr')
        if fr_elem is not None:
            bicfi_elem = None
            for el in fr_elem.iter():
                if strip_namespace(el.tag) == 'BICFI' and el.text:
                    bicfi_elem = el
                    break
            if bicfi_elem is not None:
                fr = bicfi_elem.text.strip()
            else:
                # fallback: first child text
                for child in fr_elem:
                    if child.text:
                        fr = child.text.strip()
                        break
        # To
        to_elem = get_child_text(AppHdr_elem, 'To')
        if to_elem is not None:
            bicfi_elem = None
            for el in to_elem.iter():
                if strip_namespace(el.tag) == 'BICFI' and el.text:
                    bicfi_elem = el
                    break
            if bicfi_elem is not None:
                to = bicfi_elem.text.strip()
            else:
                for child in to_elem:
                    if child.text:
                        to = child.text.strip()
                        break
        # CreDt
        credt_elem = get_child_text(AppHdr_elem, 'CreDt')
        if credt_elem is not None and credt_elem.text:
            credt = credt_elem.text.strip()
        # BizMsgIdr
        bizmsgidr_elem = get_child_text(AppHdr_elem, 'BizMsgIdr')
        if bizmsgidr_elem is not None and bizmsgidr_elem.text:
            bizmsgidr = bizmsgidr_elem.text.strip()
        # BizSvc
        bizsvc_elem = get_child_text(AppHdr_elem, 'BizSvc')
        if bizsvc_elem is not None and bizsvc_elem.text:
            bizsvc = bizsvc_elem.text.strip()
        # MsgDefIdr for XSD override
        msgdefidr_elem = get_child_text(AppHdr_elem, 'MsgDefIdr')
        if msgdefidr_elem is not None and msgdefidr_elem.text:
            msgdefidr = msgdefidr_elem.text.strip()
            xsd = msgdefidr
    return xsd, msgid, fr, to, credt, bizmsgidr, bizsvc

def parse_xml_to_xpath_and_value(file_path: str, strip_space: bool = True) -> tuple:
    """
    Parse an XML file and return a tuple:
    - list of (XPath, XPath_strip, value, file_path, file_name) tuples for all elements
    - xsd (from Document tag)
    - msgid (from MsgId tag)
    - fr, to, credt, bizmsgidr, bizsvc (from AppHdr)
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        xpaths_and_values = get_xpath_and_value(root, strip_space=strip_space)
        file_name = os.path.basename(file_path)
        # xpaths_and_values: List of (xpath, xpath_strip, value)
        results = [(xpath, xpath_strip, value, file_path, file_name) for xpath, xpath_strip, value in xpaths_and_values]
        xsd, msgid, fr, to, credt, bizmsgidr, bizsvc = extract_metadata(tree)
        return results, xsd, msgid, fr, to, credt, bizmsgidr, bizsvc
    except ET.ParseError as e:
        print(f'Error parsing XML file: {file_path} -- {e}')
        return [], '', '', '', '', '', '', ''
    except FileNotFoundError:
        print(f'File not found: {file_path}')
        return [], '', '', '', '', '', '', ''

def find_xml_files(path: str) -> List[str]:
    """Return a list of XML file paths from a directory or a single file."""
    if os.path.isfile(path) and path.lower().endswith('.xml'):
        return [os.path.abspath(path)]
    xml_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.lower().endswith('.xml'):
                xml_files.append(os.path.abspath(os.path.join(root, file)))
    return xml_files

def main():
    import sys
    
    # Parse command-line arguments
    args = sys.argv[1:]
    sort_results = False
    output_file = "xpaths.txt"
    with_labels = False
    strip_space = True

    # Check for flags
    if '--sort' in args:
        sort_results = True
        args.remove('--sort')
    if '--with-labels' in args:
        with_labels = True
        args.remove('--with-labels')
    if '--no-strip' in args:
        strip_space = False
        args.remove('--no-strip')
    
    if len(args) < 1 or len(args) > 2:
        print("Usage: python xml_to_xpath.py <xml_file_or_directory> [output_file] [--sort] [--with-labels] [--no-strip]")
        sys.exit(1)
    
    input_path = args[0]
    if len(args) == 2:
        output_file = args[1]
    
    xml_files = find_xml_files(input_path)
    if not xml_files:
        print(f"No XML files found in {input_path}")
        sys.exit(1)
    all_results = []
    file_metadata = []  # List of (xsd, msgid, fr, to, credt, bizmsgidr, bizsvc)
    for xml_file in xml_files:
        results, xsd, msgid, fr, to, credt, bizmsgidr, bizsvc = parse_xml_to_xpath_and_value(xml_file, strip_space=strip_space)
        all_results.extend(results)
        file_metadata.extend([(xsd, msgid, fr, to, credt, bizmsgidr, bizsvc)] * len(results))
    if sort_results:
        all_results, file_metadata = zip(*sorted(zip(all_results, file_metadata), key=lambda x: x[0][0])) if all_results else ([],[])

    if all_results:
        print("\nGenerated XPaths, Values, and File Info (namespaces stripped):")
        header = "XPath | XPath_strip | Value | File | Name"
        print(header)
        for xpath, xpath_strip, value, file_path, file_name in all_results:
            if with_labels:
                print(f"{xpath} | XPath_strip: {xpath_strip} | Value: {value} | File: {file_path} | Name: {file_name}")
            else:
                print(f"{xpath} | {xpath_strip} | {value} | {file_path} | {file_name}")
        # Add isEmptyValue, XSD, MsgId, AppHdr fields to output file only
        file_header = header + " | isEmptyValue | XSD | MsgId | Fr | To | CreDt | BizMsgIdr | BizSvc"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(file_header + '\n')
                for (xpath, xpath_strip, value, file_path, file_name), (xsd, msgid, fr, to, credt, bizmsgidr, bizsvc) in zip(all_results, file_metadata):
                    is_empty = str(value == '' or value is None)
                    if with_labels:
                        f.write(f"{xpath} | XPath_strip: {xpath_strip} | Value: {value} | File: {file_path} | Name: {file_name} | isEmptyValue: {is_empty} | XSD: {xsd} | MsgId: {msgid} | Fr: {fr} | To: {to} | CreDt: {credt} | BizMsgIdr: {bizmsgidr} | BizSvc: {bizsvc}\n")
                    else:
                        f.write(f"{xpath} | {xpath_strip} | {value} | {file_path} | {file_name} | {is_empty} | {xsd} | {msgid} | {fr} | {to} | {credt} | {bizmsgidr} | {bizsvc}\n")
            print(f"\nXPaths, values, and file info have been written to: {output_file}")
        except Exception as e:
            print(f"Error writing to file {output_file}: {e}")
    else:
        print("No XPaths found or error parsing XML.")

if __name__ == "__main__":
    main()
