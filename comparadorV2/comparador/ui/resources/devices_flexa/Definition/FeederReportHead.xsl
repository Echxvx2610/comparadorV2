<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:fo="http://www.w3.org/1999/XSL/Format"
	version='1.0'>

<!-- *** Root Context Start *** -->



<xsl:template match="FeederReportHeader">
<body>





		<h3>
			Job properties
		</h3>
		<table class="head">
			<xsl:apply-templates select="Header"/>
		</table>
	</body>
</xsl:template>

<!-- *** Header Context Start *** -->
<xsl:template match="Header">

<xsl:comment> ***  If position is "1" then skip process.  *** </xsl:comment>
<xsl:if test = "position() != 1">
<xsl:comment> ************************************************** </xsl:comment>


<xsl:comment> ***  barras code   *** </xsl:comment>


	
	<tr class="head">
		<th class="head"><font face='tahoma' size='5'>Codigo de Barras</font></th>
		
		<td class="head">		
			<font face='free 3 of 9' size='6'>
			 
				<xsl:text>*</xsl:text>

				<xsl:value-of select="JobName"/><xsl:text>%O</xsl:text>
				<xsl:value-of select="JobRevision"/><xsl:text>%O</xsl:text>			
				<xsl:value-of select="McName"/><xsl:text>%O</xsl:text>
				<xsl:value-of select="substring(BoardSide,1,1)"/>

				<xsl:text>*</xsl:text>

			</font><br/>
		</td>		
	</tr>	


<xsl:comment> ***  Machine  *** </xsl:comment>
	<tr class="head">
		<th class="head">Machine</th>
		<td class="head"><xsl:value-of select="McName"/><br/></td>
	</tr>

<xsl:comment> ***  Recipe Name  *** </xsl:comment>
	<tr class="head">
		<th class="head">Recipe name</th>
		<td class="head"><xsl:value-of select="prgName"/><br/></td>
	</tr>

<xsl:comment> ***  Revision *** </xsl:comment>
	<tr class="head">
		<th class="head">Revision</th>
		<td class="head"><xsl:value-of select="JobRevision"/><br/></td>
	</tr>

<xsl:comment> ***  Job Comment *** </xsl:comment>
	<tr class="head">
		<th class="head">Job Comment</th>
		<td class="head"><xsl:value-of select="JobComment"/><br/></td>
	</tr>

<xsl:comment> ***  Author *** </xsl:comment>
	<tr class="head">
		<th class="head">Author</th>
		<td class="head"><xsl:value-of select="JobAuthor"/><br/></td>
	</tr>

<xsl:comment> ***  Date *** </xsl:comment>
	<tr class="head">
		<th class="head">Date</th>
		<td class="head"><xsl:value-of select="RepDate"/><br/></td>
	</tr>

<xsl:comment> ***  Time *** </xsl:comment>
	<tr class="head">
		<th class="head">Time</th>
		<td class="head"><xsl:value-of select="RepTime"/><br/></td>
	</tr>

<xsl:comment> ***  Panel Length (X) *** </xsl:comment>
	<tr class="head">
		<th class="head">Panel length (X)</th>
		<td class="head"><xsl:value-of select="prgPnlLength"/><br/></td>
	</tr>

<xsl:comment> ***  Panel Width (Y) *** </xsl:comment>
	<tr class="head">
		<th class="head">Panel width (Y)</th>
		<td class="head"><xsl:value-of select="prgPnlWidth"/><br/></td>
	</tr>

<xsl:comment> ***  Thickness *** </xsl:comment>
	<tr class="head">
		<th class="head">Thickness</th>
		<td class="head"><xsl:value-of select="prgPnlThickness"/><br/></td>
	</tr>

<xsl:comment> *** Panel Roation *** </xsl:comment>
	<xsl:if test="count(//prgProcPnlRotation)">
	<tr class="head">
		<th class="head">Panel Roation</th>
		<td class="head">
			<xsl:choose>
			<xsl:when test="prgProcPnlRotation='0'">0deg</xsl:when>
			<xsl:when test="prgProcPnlRotation='1'">90deg</xsl:when>
			<xsl:when test="prgProcPnlRotation='2'">180deg</xsl:when>
			<xsl:when test="prgProcPnlRotation='3'">270deg</xsl:when>
			</xsl:choose>
		</td>
	</tr>
	</xsl:if>

<xsl:comment> ***  Side *** </xsl:comment>
	<tr class="head">
		<th class="head">Side</th>
		<td class="head"><xsl:value-of select="BoardSide"/><br/></td>
	</tr>

<xsl:comment> *** Production Quantity *** </xsl:comment>
	<tr class="head">
		<th class="head">Production Quantity</th>
		<td class="head"><xsl:value-of select="prgProdQty"/><br/></td>
	</tr>

<xsl:comment> *** Total Components *** </xsl:comment>
	<tr class="head">
		<th class="head">Total components</th>
		<td class="head"><xsl:value-of select="TotalNoOfComponents"/><br/></td>
	</tr>

<xsl:comment> *** Total Feeders *** </xsl:comment>
	<tr class="head">
		<th class="head">Total feeders</th>
		<td class="head"><xsl:value-of select="TotalNoOfFeeders"/><br/></td>
	</tr>

<xsl:comment> ************************************************** </xsl:comment>
</xsl:if>

</xsl:template>

</xsl:stylesheet>
