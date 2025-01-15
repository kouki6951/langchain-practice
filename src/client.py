######################################################################
# Serving with LangServe
# client.py
# 実行方法に関してはREADMEを参照
######################################################################

from langserve import RemoteRunnable

remote_chain = RemoteRunnable("http://localhost:8001/chain/")
result = remote_chain.invoke({"language": "italian", "text": "hi"})
print(result)