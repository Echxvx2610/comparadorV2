function ReplaceInnerHTML(id, xmlSrc, xslSrc)
{
	try
	{
		// XML/XSL�h�L�������g�̃��[�h
		var xmlObj, xslObj;
		var Version = "";
		try
		{
			xmlObj = new ActiveXObject("MSXML2.DOMDocument.6.0");						// MSXML6.0��
			xslObj = new ActiveXObject("MSXML2.DOMDocument.6.0");
			Version = "MSXML6.0";
		} catch(e) {
			try
			{
				xmlObj = new ActiveXObject("MSXML2.DOMDocument.4.0");					// MSXML4.0��
				xslObj = new ActiveXObject("MSXML2.DOMDocument.4.0");
				Version = "MSXML4.0";
			} catch(e) {
				try
				{
					xmlObj = new ActiveXObject("MSXML2.DOMDocument");					// MSXML3.0��
					xslObj = new ActiveXObject("MSXML2.DOMDocument");
					Version = "MSXML3.0";
				} catch(e) {
					try
					{
						xmlObj = new ActiveXObject("MSXML.DOMDocument");				// MSXML2.0��
						xslObj = new ActiveXObject("MSXML.DOMDocument");
						Version = "MSXML2.0";
					} catch(e) {
						xmlObj = document.implementation.createDocument("", "", null);	// FireFox��
						xslObj = document.implementation.createDocument("", "", null);
						Version = "FireFox";
					}
				}
			}
		}
		if(Version.length == 0) return false;
		// alert("XML�p�[�T�̃o�[�W������ " + Version + " �ł��B");
		xmlObj.async = false;
		xslObj.async = false;
		xmlObj.load(xmlSrc);
		xslObj.load(xslSrc);

		// ����HTML�̒u������(IE11�Ή��ς�)
		document.getElementById(id).innerHTML = xmlObj.transformNode(xslObj);
	} catch(e) {
	}
}

// �ȉ��A���܂����삵�Ȃ���������
//	�� �ꉞ�A�o�b�N�A�b�v���Ă���
/*
function createXmlhttp()
{
	var xmlhttp = false;
	if(typeof XMLHttpRequest != "undefined")
	{
		// IE7�ȍ~, Firefox, Safari
		xmlhttp = new XMLHttpRequest();
	}
	if(!xmlhttp && typeof ActiveXObject != "undefined")
	{
		// IE5, 6
		try
		{
			xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");		// MSXML3
		} catch (e) {
			xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");	// MSXML2
		}
	}
	if(!xmlhttp)
	{
		return false;
	}

	return xmlhttp;
}

function ReplaceInnerHTML(id, xmlSrc, xslSrc)
{
	var xmlhttp = new createXmlhttp();
	var xslhttp = new createXmlhttp();
	var oSource;
	var oStyle;
	var disp = document.getElementById(id);
	if(xmlhttp)
	{
		xmlhttp.open("GET", xmlSrc);
		xmlhttp.onreadystatechange = function()
		{
//			if(xmlhttp.readyState == 4 && xmlhttp.status == 200)
			if(xmlhttp.readyState == 4)
			{
				oSource = xmlhttp.responseXML;
			}
		}
		xmlhttp.send(null);
	}
	if(xslhttp)
	{
		xslhttp.open("GET", xslSrc);
		xslhttp.onreadystatechange = function()
		{
//			if(xslhttp.readyState == 4 && xslhttp.status == 200)
			if(xslhttp.readyState == 4)
			{
				oStyle = xslhttp.responseXML;
				var u = new Ajaxslt(oStyle);
				u.transformToHTML(oSource, disp);
			}
		}
		xslhttp.send(null);
	}
}

function Ajaxslt(a)
{
	this.stylesheet = a;
}

Ajaxslt.prototype.transformToHTML = function(a, b)
{
	if(typeof a.transformNode != "undefined")
	{
		// IE
		b.innerHTML = a.transformNode(this.stylesheet);
	}
	else if(typeof XSLTProcessor != "undefined" && typeof XSLTProcessor.prototype.importStylesheet != "undefined")
	{
		// Firefox, Safari
		var c = new XSLTProcessor();
		c.importStylesheet(this.stylesheet);
		var d = c.transformToFragment(a, window.document);
		b.innerHTML = "";
		b.appendChild(d);
	}
}
*/