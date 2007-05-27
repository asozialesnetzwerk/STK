<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  
  <xsl:output 
    method="html" 
    indent="yes" 
    doctype-public="-//W3C//DTD HTML 4.01//EN" 
    doctype-system="http://www.w3.org/TR/html4/strict.dtd"
    encoding="ISO-8859-1" />

  <xsl:param name="filename"/>
  <xsl:param name="lastchange"/>  
  <xsl:param name="group" select="/page/@group" />  
  
  <xsl:template match="node()|@*">
    <xsl:copy><xsl:apply-templates select="@* | node()" /></xsl:copy>
  </xsl:template>

  <xsl:template match="page">
    <html>
      <head>
        <title>SuperTuxKart - A Kart Game Featuring Tux and Friends</title>
        <link rel="stylesheet" type="text/css" href="default.css" />
        <link rel="icon" href="images/favicon.png" type="image/png" />
      </head>

      <body>
        <table width="100%" border="0" style="margin: 0em; padding: 0em;">
          <tr>
            <td align="left">
              <img src="images/supertuxkart.png" alt="SuperTuxKart" />              
            </td>
            <td align="center" valign="middle">
              <h2 style="font-size: 3.5em; font-weight: bold;"><u><b><i>..:: 
                      <xsl:value-of select="/page/@title" />
                      ::..</i></b></u></h2>
              </td>
            <td align="right" valign="bottom">
              <img src="images/tux.png" alt="" />
            </td>
          </tr>
        </table>
       
        <table width="100%" cellspacing="0" cellpadding="0" border="0" align="center" style="margin-bottom: 0em;">
          <tr>
            <td valign="top" width="200">
              <xsl:apply-templates select="document('menu.xml')" />
            </td>
            <td>
              <div class="body">
              <xsl:apply-templates />
              </div>
            </td>
          </tr>
        </table>
        
        <div class="copyright">
          Copyright &#0169; 2004 SuperTuxKart Development Team<br />
          Last update: <xsl:value-of select="$lastchange" /><br />
        </div>
      </body>
    </html>
  </xsl:template>
  
  <xsl:template match="section">
    <div class="section-box">
      <xsl:if test="@id!=''">
        <xsl:attribute name="id"><xsl:value-of select="@id" /></xsl:attribute>
      </xsl:if>
      <div class="section-title"><h2><xsl:value-of select="@title" /></h2></div>
      <div class="section-body">
        <xsl:apply-templates />
      </div>
    </div>
  </xsl:template>

  <xsl:template match="subsection">
    <h3><xsl:value-of select="@title" /></h3>
    <xsl:apply-templates />
    <br clear="all" />
  </xsl:template>

  <xsl:template match="subsubsection">
    <div style="padding-left: 1em; clear: both;">
      <h4><xsl:value-of select="@title" /></h4>
      <xsl:apply-templates />
    </div>
  </xsl:template>

  <xsl:template match="faq-list">
    <ul>
      <xsl:for-each select="faq/question">
        <li><a href="#faq{generate-id(.)}">
            <xsl:apply-templates/></a></li>
      </xsl:for-each>
    </ul>
    <hr/>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="faq">
    <p></p>
    <table width="100%"  class="question">
      <colgroup width="60%" />
      <tr><td valign="top">
          <div id="faq{generate-id(question)}">
            <xsl:apply-templates select="question/node()"/>
          </div>
        </td>
        
        
        <td align="right" valign="top">
          <small>Last update:<xsl:value-of select="@date"/></small>
          [<small><a href="#faqtoc">Up</a></small>]
        </td>
      </tr>
    </table>

    <p class="answer"><xsl:apply-templates select="answer/node()"/> </p>
  </xsl:template>
  
  <xsl:template match="news">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="news/item">
    <p style="padding: 0em;"><strong><xsl:value-of select="@date" /></strong> - <xsl:apply-templates /></p>
  </xsl:template>

  <!-- Menu Stuff -->
  <xsl:template match="menu">
    <div class="menu">
      <xsl:apply-templates />
    </div>
  </xsl:template>

  <xsl:template match="menu/item">
    <div>
      <xsl:choose>
        <xsl:when test="concat($group, '.html')=@file or concat($filename, '.html')=@file">
          <a class="active" href="{@file}"><xsl:apply-templates /></a>
        </xsl:when>
        <xsl:otherwise>
        <a href="{@file}"><xsl:apply-templates /></a>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <!-- Submenu Stuff -->
  <xsl:template match="submenu">
    <div class="submenu">
      <table cellpadding="0" cellspacing="0" border="0" align="center">
        <tr>
          <xsl:apply-templates />
        </tr>
      </table>
    </div>
  </xsl:template>

  <xsl:template match="submenu/item">
    <td>
      <xsl:choose>
        <xsl:when test="concat($filename, '.html')=@file">
          <a class="active" href="{@file}"><xsl:apply-templates /></a>
        </xsl:when>
        <xsl:otherwise>
          <a href="{@file}"><xsl:apply-templates /></a>
        </xsl:otherwise>
      </xsl:choose>
    </td>
  </xsl:template>


</xsl:stylesheet>