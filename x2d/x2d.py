#!/usr/bin/python

# @file x2d.py
# @author cherezov.pavel@gmail.com
# @brief XML to python dict converter with xpath-like access

# Change log:
# 1.0 Initial version

import re

__version__ = 1.0

def get_tag_value(x):
   """ Get xml tag name.

   x -- xml string
   ignoreUntilXML - skip symbols until '<'
   return -- (tag, value, rest_string)
      e.g
         <d>
            <e>value4</e>
         </d>_rest_string
      result is ('d', '<e>value4</e>', '_rest_text_')
   """
   i = 0
   tag = ''
   value = ''

   # skip all symbols until < tag
   while i < len(x) and x[i] != '<':
      i += 1

   # skip <? > tag
   if x[i:].startswith('<?'):
      i += 2
      while i < len(x) and x[i] != '<':
         i += 1

   # check for empty tag like '</tag>'
   if x[i:].startswith('</'):
      i += 2
      in_attr = False
      while i < len(x) and x[i] != '>':
         if x[i] == ' ':
            in_attr = True
         if not in_attr:
            tag += x[i]
         i += 1
      return (tag.strip(), '', x[i+1:])

   # not an xml, treat it like a value
   if not x[i:].startswith('<'):
      return ('', x[i:], '')

   i += 1 # <

   # read first open tag
   in_attr = False
   while i < len(x) and x[i] != '>':
      # get rid of attributes
      if x[i] == ' ':
         in_attr = True
      if not in_attr:
         tag += x[i]
      i += 1

   i += 1 # >

   while i < len(x):
      value += x[i]
      if x[i] == '>' and value.endswith('</' + tag + '>'):
         # Note: will not work with xml like <a> <a></a> </a>
         close_tag_len = len(tag) + 2 # />
         value = value[:-close_tag_len]
         break
      i += 1
   return (tag.strip(), value[:-1], x[i+1:])

def xml2dict(s, ignoreUntilXML = False):
   """ Convert xml to dictionary.
   """
   if ignoreUntilXML:
      s = ''.join(re.findall(".*?(<.*)", s, re.M))

   d = {}
   while s:
      tag, value, s = get_tag_value(s)
      value = value.strip()
      isXml, dummy, dummy2 = get_tag_value(value)
      if tag not in d:
         d[tag] = []
      if not isXml:
         if not value:
            continue
         d[tag].append(value.strip())
      else:
         if tag not in d:
            d[tag] = []
         d[tag].append(xml2dict(value))
   return d

def xpath(d, path):
   """ Return value from xml dictionary at path.

   d -- xml dictionary
   path -- string path like a/b/c@d=val/e
   return -- value at path or None if path not found
   """

   if isinstance(d, str):
      d = xml2dict(d)

   for p in path.split('/'):
      tag_attr = p.split('@')
      tag = tag_attr[0]
      if tag not in d:
         return None

      attr = tag_attr[1] if len(tag_attr) > 1 else ''
      if attr:
         a, aval = attr.split('=')
         for s in d[tag]:
            if s[a] == [aval]:
               d = s
               break
      else:
         d = d[tag][0]
   return d

if __name__ == '__main__':
   import unittest

   class TestX2D(unittest.TestCase):
      def test_TagValue(self):
         s = "<a>val</a>"
         tag, value, rest = get_tag_value(s)
         self.assertEqual(tag, 'a')
         self.assertEqual(value, 'val')
         self.assertEqual(rest, '')

         s = "<a>val</a>_rest_text_"
         tag, value, rest = get_tag_value(s)
         self.assertEqual(tag, 'a')
         self.assertEqual(value, 'val')
         self.assertEqual(rest, '_rest_text_')

         s = "<a> </a>_rest_text_"
         tag, value, rest = get_tag_value(s)
         self.assertEqual(tag, 'a')
         self.assertEqual(value, ' ')
         self.assertEqual(rest, '_rest_text_')

         s = "<a><b>value</b></a>_rest_text_"
         tag, value, rest = get_tag_value(s)
         self.assertEqual(tag, 'a')
         self.assertEqual(value, '<b>value</b>')
         self.assertEqual(rest, '_rest_text_')

         s = "_bad prefix! <a><b>value</b></a>_rest_text_"
         tag, value, rest = get_tag_value(s)
         self.assertEqual(tag, 'a')
         self.assertEqual(value, '<b>value</b>')
         self.assertEqual(rest, '_rest_text_')

         s = "<?this must be skipped><a attr='this must be skipped as well'><b>value</b></a>_rest_text_"
         tag, value, rest = get_tag_value(s)
         self.assertEqual(tag, 'a')
         self.assertEqual(value, '<b>value</b>')
         self.assertEqual(rest, '_rest_text_')

      def test_TagValueEmptyVal(self):
         s = "<a></a>_rest_text_"
         tag, value, rest = get_tag_value(s)
         self.assertEqual(tag, 'a')
         self.assertEqual(value, '')
         self.assertEqual(rest, '_rest_text_')

         s = "</a>_rest_text_"
         tag, value, rest = get_tag_value(s)
         self.assertEqual(tag, 'a')
         self.assertEqual(value, '')
         self.assertEqual(rest, '_rest_text_')

      def test_Xml2Dict(self):
         s = "<a>val</a>"
         d = xml2dict(s)
         self.assertEqual(d, { 'a' : ['val'] } )

         s = "</a>"
         d = xml2dict(s)
         self.assertEqual(d, { 'a' : [] } )

         s = "<a></a>"
         d = xml2dict(s)
         self.assertEqual(d, { 'a' : [] } )

         s = "<a>val1</a> <a>val2</a>"
         d = xml2dict(s)
         self.assertEqual(d, { 'a' : ['val1', 'val2'] } )

         s = "<a>val1</a> <a>val2</a>"
         d = xml2dict(s)
         self.assertEqual(d, { 'a' : ['val1', 'val2'] } )

         s = "<a><b>val</b></a>"
         d = xml2dict(s)
         self.assertEqual(d, { 'a' : [{'b' : ['val'] }] } )

      def test_XPath(self):
         s = "<a>val</a>"
         val = xpath(s, 'a')
         self.assertEqual(val, 'val')

         s = "<a><b>val</b></a>"
         val = xpath(s, 'a/b')
         self.assertEqual(val, 'val')

         s = """<a>
                     <b>
                        <c>BAD VAL</c>
                        <d>BAD VAL</d>
                     </b>

                     <b>
                        <c>find me</c>
                        <d>val</d>
                     </b>
                </a>
         """
         val = xpath(s, 'a/b@c=find me/d')
         self.assertEqual(val, 'val')

      def test_BadXPath(self):
         s = "<a>val</a>"
         val = xpath(s, 'b')
         self.assertEqual(val, None)

   unittest.main()
