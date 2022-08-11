# 準備
`cd ~/work`

`python3 -m venv env/azuredevops`

`source env/azuredevops/bin/activate`

`cd azuredevops/`

`pip install requests`

`pip install openpyxl`

# トークンを作成

# settings_app.jsonを作成しルートディレクトリに格納
`vi ./settings_app.json`


```
{
    "ads": {
        "url_core": "https://dev.azure.com/",
        "organization": "xxxx",
        "project": "yyyy",
        "id": "zzzzz",
        "pw": "tttttttttttttttttttttttttttttt",
        "api_version": "6.0"
    } 
}
```