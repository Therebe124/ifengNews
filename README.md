# ifengNews
联系程序，目标:获取链接目标中的新闻信息（包括title，time，content，img等等）
使用scrapy进行数据的获取

启动:可以运行start.py

主要程序——spiders/ifnews.py:
	初始url:start_url,
	使用rules，规定了抓取url的区域:restrict_xpath
	因为列表中的新闻url主要分为两种:
	http://news.ifeng.com/a/20150408/43506164_0.shtml，
	http://news.ifeng.com/photo/hdsociety/detail_2015_04/08/40995118_0.shtml，
	所以对于url进行判断， LinkExtractor(allow='')
	1、allow=r.'.*/a/*' 此类文章主要以文本为主，部分文章中存在图片:
		callback=parse_a
		parse_a方法中：
			从html的head中获取time、title:
				xpath('//head/meta[@name="og:time"]/@content')
				xpath('//head/meta[@property="og:title"]/@content')
			从response中获取url:
				response.url
			根据id="main_content"获取正文信息:
				xpath('//div[@id="main_content"]/p[not(@*)]/text()')
				部分社会话题由于网页布局不同：http://news.ifeng.com/a/20150408/43506054_0.shtml
				xpath('//div[@class="wrapIphone AtxtType01"]/p[not(@*)]/text()')
				最后对获取的文章进行拼接
			根据class=detailPic进行图片链接的获取:
				xpath('//div[@id="main_content"]/p[@class="detailPic"]/img/@src')
			根据class=picIntro进行图片描述的获取:
				xpath('//div[@id="main_content"]/p[@class="picIntro"]/span/text()')

	2、allow=r'.*/photo/*' 此类文章以组图为主:
		callback=pares_photo
		pares_photo方法中:
			因为html的head中内容不足，所以通过标签<h1><h4>分别获取title和time:
				xpath('//h1/text()').get()
				xpath('//h4/text()').get()
			从response中获取url:
				response.url
			文章中没有content，置空:
				item['content']=""
			因为是组图原因，页面中能获取全部图片和描述的部分为<script>:
				<script type="text/javascript">
					var _listdata= [];
						_listdata[0] = {title:'',timg:'',img:'',listimg:'',picwidth:'',picheight:'',morelink:''}
						_listdata[1] = {title:'',timg:'',img:'',listimg:'',picwidth:'',picheight:'',morelink:''}
						.
						.
						.
				</script>
			所以通过判断取出img和img_details:
				xpath('//script[6]/text()').get()
				img = r', img: (.*?), listimg'
				details =  r'title: (.*?), timg'
	3、allow=r'.*/rt-channel/*' 此为获取当前日期的“下一页”的url

数据格式——items.py:
	title,time,content,url,img,img_details

数据保存到数据库中——pipelines.py:
	链接数据库中的db——ifeng:
	新建表article——number设为自增主键，origin_url为唯一索引:
		CREATE TABLE `ifeng`.`article` (
  			`number` INT(11) NOT NULL,
 			`pub_time` VARCHAR(255) NULL DEFAULT NULL,
			`title` VARCHAR(255) NULL DEFAULT NULL,
			`content` LONGTEXT NULL DEFAULT NULL,
			`origin_url` VARCHAR(255) NULL DEFAULT NULL,
			`img` LONGTEXT NULL DEFAULT NULL,
			`img_datails` LONGTEXT NULL DEFAULT NULL,
			PRIMARY KEY (`number`),
			UNIQUE INDEX `origin_url_UNIQUE` (`origin_url` ASC) VISIBLE);

		调试可能需要的sql操作:
		SELECT * FROM ifeng.article;
		truncate table ifeng.article;

配置文件——settings.py:
			
			ROBOTSTXT_OBEY = False
			
			DEFAULT_REQUEST_HEADERS = {
		   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		   'Accept-Language': 'en',
		   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
		}

	head信息有待完善
	因为待爬取的网站目前没碰到反爬机制。（有待确认中）

存在问题:
 《凤凰热追踪》文章格式待整理:http://news.ifeng.com/a/20150407/43497980_0.shtml
 时间格式:页面中没有详细的时间

正在进行中的工作:
	如何自动获取到前一天的url:
		可以在最后一个<script>中获取到
	增加redis或者mongodb断点续爬


