<p align="center">
 📦 <a href="https://pypi.org/project/telegrams" style="text-decoration:none;">Telegrams</a>
</p>


```python

from Telegrams.functions import Telegraph

telegraph = Telegraph()
telegraph.create_account(short_name='1337')

response = telegraph.create_page('Hey', html_content='<p>Hello, world!</p>')

print(response['url'])

```
