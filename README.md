# x2d
Xml to dictionary converter with xpath-like access
Attributes are ignored.

## Example
### 1
```python
import x2d
s = "<a> <b>value1</b> <b>value2</b> </a>"
d = x2d.xml2dict(s)
```
will result ```{'a' : [{ 'b': ['value1', 'value2'] }] }```

### 2
```python
import x2d
s = "<a> <b>value</b> </a>"
val = x2d.xpath(s, 'a/b')
```
will find ```value```

### 3
```python
import x2d
s = """<a>
  <b>
    <c>not interested</c>
    <d>not interested</d>
  </b>
  
  <b>
    <c>c_value</c>
    <d>d_value</d>
  </b>
</a>
"""
val = x2d.xpath(s, 'a/b@c=c_value/d')
```
will find ```d_value```
