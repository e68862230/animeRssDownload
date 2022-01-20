document.addEventListener('DOMContentLoaded', function() {
	var defaultConfig = {username: '123', password: '123',ipPort:'http://127.0.0.1:8000/',qbPort:'https://127.0.0.1:8080'}; // 默认配置
	// 读取数据，第一个参数是指定要读取的key以及设置默认值
	chrome.storage.sync.get(defaultConfig, function(items) {
		document.getElementById('username').value = items.username;
		document.getElementById('password').value = items.password;
		document.getElementById('ipPort').value = items.ipPort;
		document.getElementById('qbPort').value = items.qbPort;
	});
});

document.getElementById('save').addEventListener('click', function() {
	var username = document.getElementById('username').value;
	var password = document.getElementById('password').value;
	var ipPort = document.getElementById('ipPort').value;
	var qbPort = document.getElementById('qbPort').value;
	// 这里貌似会存在刷新不及时的问题
	chrome.storage.sync.set({username: username, password: password,ipPort:ipPort,qbPort:qbPort}, function() {
		document.getElementById('status').textContent = '保存成功！';
		setTimeout(() => {document.getElementById('status').textContent = '';}, 800);
	});
});