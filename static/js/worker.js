// 在结果列表窗口增加结果项目，好推动进一步向下进行。	
function add_list_item(id,title,url){
    li = $('<li class="item"><input type = "checkbox"/><div class = "title">标题</div> <div>...</div><button class = "btn_go">下一步</button> </li>');	
    $('#itemlist').append(li);
    $(li.childNodes[0] ).attr('checked', true)
    $(li.childNodes[1]).text(title);	
    $(li.childNodes[2]).click({mhid:id},start_long_task);

    /** 改变页面元素属性的方法
    $("img").attr({ 
        src: "/images/logo.gif", 
        title: "jquery", 
        alt: "jquery" 
    }); 
    $("div").text($("img").attr("alt")); 
    **/
    	
}
// 请求 longtask 接口	
function start_long_task(data) {	
            // 添加元素在html中	
            console.debug(data);

            div = $('<div class="progress"><div></div><div>0%</div><div>...</div><div>&nbsp;</div></div><hr>');	
            $('#progress').append(div);	
            // 创建进度条对象	
            var nanobar = new Nanobar({	
                bg: '#44f',	
                target: div[0].childNodes[0]	
            });	
            // ajax请求jobs
            $.ajax({	
                type: 'POST',	
                url: data.url,
                //contentType: "application/json", //必须这样写
                //dataType:"json",
                //data:JSON.stringify(data.param),//schoolList是你要提交是json字符串
                data:data.param,	
                // 获得数据，从响应头中获取Location	
                success: function(data, status, request) {	
                    status_url = request.getResponseHeader('Location');	
                    // 调用 update_progress() 方法更新进度条	
                    update_progress(status_url, nanobar, div[0]);	
                },	
                error: function() {	
                    alert(' 发生不明错误');	
                }	
            });	 
        }	

// 更新进度条	
function update_progress(status_url, nanobar, status_div) {	
            // getJSON()方法是JQuery内置方法，这里向Location中对应的url发起请求，即请求「/status/<task_id>」	
            $.getJSON(status_url, function(data) {	
                // 计算进度	
                percent = parseInt(data['current'] * 100 / data['total']);	
                // 更新进度条	
                nanobar.go(percent);	
                // 更新文字	
                $(status_div.childNodes[1]).text(percent + '%');	
                $(status_div.childNodes[2]).text(data['status']);	
                if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {	
                    if ('result' in data) {	
                        // 展示结果	
                        $(status_div.childNodes[3]).text('Result: ' + data['result']);	
                    }	
                    else {	
                        // 意料之外的事情发生	
                        $(status_div.childNodes[3]).text('Result: ' + data['state']);	
                    }	
                }	
                else {	
                    // 2秒后再次运行	
                    setTimeout(function() {	
                        update_progress(status_url, nanobar, status_div);	
                    }, 1000);	
                }	
            });	
        }

