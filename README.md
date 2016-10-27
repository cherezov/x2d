# x2d
Xml to dictionary converter with xpath-like access

## Example
```python
import x2d
s = "<a> <b>value</b> </a>"
val = xpath(s, 'a/b')
```
will find ```value```

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
val = xpath(s, 'a/b@c=c_value/d')
```
will find ```d_value```
