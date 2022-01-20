// background.js
chrome.contextMenus.create({
    title: '下载RSS到服务器', // %s表示选中的文字
    contexts: ['link'], // 只有当选中文字时才会出现此右键菜单
    onclick: function(params)
    {
    // 注意不能使用location.href，因为location是属于background的window对象
    //alert('RSS链接创建中')
    //alert(params.linkUrl)
    //alert(params.selectionText)
    chrome.notifications.create(params.selectionText, {
    type: 'basic',
    title: 'RSS下载器',
    message: '下载中',
    iconUrl: "icons/icon-128.png"
   });
    var username='';
    var password='';
    var ipPort='';
    var qbPort='';
	// 读取数据，第一个参数是指定要读取的key以及设置默认值
    var defaultConfig = {username: '123', password: '123',ipPort:'',qbPort:''}; // 默认配置
	// 读取数据，第一个参数是指定要读取的key以及设置默认值
	chrome.storage.sync.get(defaultConfig, function(items) {
		username = items.username;
		password = items.password;
		ipPort = items.ipPort;
		qbPort=items.qbPort;
		console.log(username+password+ipPort+qbPort)
        var postParams={'username':username,'password':password,'rssUrl':params.linkUrl,'qbPort':qbPort}
            var aj=$.ajax({
                type:"POST",  //请求方式
                url:ipPort,  //请求路径：页面/方法名字
                data: JSON.stringify(postParams),     //参数
                dataType:"json",
                contentType:"application/json; charset=utf-8",
                success:function(msg){  //成功
                    chrome.notifications.create(params.selectionText, {
                            type: 'basic',
                            title: 'RSS下载器',
                            message: msg['message'],
                            iconUrl: "icons/icon-128.png"
                           });
                },
                error:function(){   //异常
                    chrome.notifications.create(params.selectionText, {
                            type: 'basic',
                            title: 'RSS下载器',
                            message: '失败',
                            iconUrl: "icons/icon-128.png"
                           });
                }
            });
	});


    //chrome.tabs.create({url: 'http://127.0.0.1:8000'});
    //chrome.tabs.create({url: 'https://www.baidu.com/s?ie=utf-8&wd=' + encodeURI(params.selectionText)
    }
   });
