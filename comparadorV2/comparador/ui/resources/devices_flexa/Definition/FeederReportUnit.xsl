<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:fo="http://www.w3.org/1999/XSL/Format" version='1.0'>

<!-- *** Root Context Start *** -->
<xsl:template match="FeederReportUnit">
	<body>
		<h3>Feeder setup</h3>
		<table class="unit">
			<xsl:apply-templates select="Title"/>
			<xsl:apply-templates select="Unit">
				<xsl:sort select="ModuleNum" data-type="number"/>
				<xsl:sort select="DisplayOrder" data-type="number"/>
			</xsl:apply-templates>
		</table>
	</body>
</xsl:template>

<!-- *** Unit Context Start *** -->
<xsl:template match="Title|Unit">
<tr class="unit">

<xsl:comment> *** Pos. *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//fsSetPos)">
			<xsl:choose>
				<xsl:when test="fsSetPos='fsSetPos'">
					<th class="unit">Pos.</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><nobr><xsl:value-of select="fsSetPos"/></nobr></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  AVL Name  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//fsAVLName)">
			<xsl:choose>
				<xsl:when test="fsAVLName='fsAVLName'">
					<th class="unit">AVL Name</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="fsAVLName"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Part Number  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//fsPartNum)">
			<xsl:choose>
				<xsl:when test="fsPartNum='fsPartNum'">
					<th class="unit">Part Num</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="fsPartNum"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Shape  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//asAsmShape)">
			<xsl:choose>
				<xsl:when test="asAsmShape='asAsmShape'">
					<th class="unit">Shape</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="asAsmShape"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Package  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pkgPkg)">
			<xsl:choose>
				<xsl:when test="pkgPkg='pkgPkg'">
					<th class="unit">Package</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="pkgPkg"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Feeder  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//fsFdrName)">
				<xsl:choose>
					<xsl:when test="fsFdrName='fsFdrName'">
						<th class="unit">Feeder</th>
					</xsl:when>
					<xsl:otherwise>
						<td class="unit"><xsl:value-of select="fsFdrName"/></td>
					</xsl:otherwise>
				</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Type  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pkgInfoPkgType)">
				<xsl:choose>
					<xsl:when test="pkgInfoPkgType='pkgInfoPkgType'">
						<th class="unit">Type</th>
					</xsl:when>
					<xsl:when test="fsPartNum=''">
						<td class="unit"><xsl:value-of select="favFdrPkg"/></td>
					</xsl:when>
					<xsl:otherwise>
						<td class="unit"><xsl:value-of select="pkgInfoPkgType"/></td>
					</xsl:otherwise>
				</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Width  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pkgInfoTapeWidth)">
			<xsl:choose>
				<xsl:when test="pkgInfoTapeWidth='pkgInfoTapeWidth'">
					<th class="unit right">Width</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit right">
					<xsl:choose>
						<xsl:when test="pkgInfoPkgType='TRAY'">
							--
						</xsl:when>
						<xsl:when test="pkgInfoPkgType='Tray'">
							--
						</xsl:when>
						<xsl:when test="pkgInfoPkgType='WAFER'">
							--
						</xsl:when>
						<xsl:when test="pkgInfoPkgType='Wafer'">
							--
						</xsl:when>
						<xsl:when test="fsPartNum=''">
							<xsl:choose>
								<xsl:when test="favFdrPkg='TRAY'">
									--
								</xsl:when>
								<xsl:when test="favFdrPkg='Tray'">
									--
								</xsl:when>
								<xsl:otherwise>
									<xsl:value-of select="favReelWidth"/>mm
								</xsl:otherwise>
							</xsl:choose>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="pkgInfoTapeWidth"/>
						</xsl:otherwise>
					</xsl:choose>
					</td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Feed Pitch  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pkgInfoFeedPitch)">
			<xsl:choose>
				<xsl:when test="pkgInfoFeedPitch='pkgInfoFeedPitch'">
					<th class="unit right">Feed Pitch</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit right">
					<xsl:choose>
						<xsl:when test="fsPartNum=''">
							--
						</xsl:when>
						<xsl:when test="pkgInfoPkgType='TRAY'">
							--
						</xsl:when>
						<xsl:when test="pkgInfoPkgType='Tray'">
							--
						</xsl:when>
						<xsl:when test="pkgInfoPkgType='WAFER'">
							--
						</xsl:when>
						<xsl:when test="pkgInfoPkgType='Wafer'">
							--
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="pkgInfoFeedPitch"/>
						</xsl:otherwise>
					</xsl:choose>
					</td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Part Height  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//asBodyHeight)">
			<xsl:choose>
				<xsl:when test="asBodyHeight='asBodyHeight'">
					<th class="unit right">Part Height</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit right"><xsl:value-of select="asBodyHeight"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Slot Status  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//fsStatus)">
			<xsl:choose>
				<xsl:when test="fsStatus='fsStatus'">
					<th class="unit">Status</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="fsStatus"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Qty  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//fsPartQty)">
			<xsl:choose>
				<xsl:when test="fsPartQty='fsPartQty'">
					<th class="unit right">Qty</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit right"><xsl:value-of select="fsPartQty"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Tray dir  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//fsTrayDir)">
			<xsl:choose>
				<xsl:when test="fsTrayDir='fsTrayDir'">
					<th class="unit">Tray dir</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit">
					<xsl:choose>
						<xsl:when test="pkgInfoPkgType='Tray'">
							<xsl:choose>
								<xsl:when test="fsTrayDir='0'">0deg</xsl:when>
								<xsl:when test="fsTrayDir='1'">90deg</xsl:when>
								<xsl:when test="fsTrayDir='2'">180deg</xsl:when>
								<xsl:when test="fsTrayDir='3'">270deg</xsl:when>
							</xsl:choose>
						</xsl:when>
						<xsl:when test="pkgInfoPkgType='TRAY'">
							<xsl:choose>
								<xsl:when test="fsTrayDir='0'">0deg</xsl:when>
								<xsl:when test="fsTrayDir='1'">90deg</xsl:when>
								<xsl:when test="fsTrayDir='2'">180deg</xsl:when>
								<xsl:when test="fsTrayDir='3'">270deg</xsl:when>
							</xsl:choose>
						</xsl:when>
						<xsl:otherwise>
							--
						</xsl:otherwise>
					</xsl:choose>
					</td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<!--
<xsl:comment> ***  Vision Type  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//asVsnVsnType)">
			<xsl:choose>
				<xsl:when test="asVsnVsnType='asVsnVsnType'">
					<th class="unit">Vision Type</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="asVsnVsnType"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>
-->

<!--
<xsl:comment> ***  Direction  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnDir)">
			<xsl:choose>
				<xsl:when test="pnDir='pnDir'">
					<th class="unit">Direction</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="pnDir"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>
-->

<xsl:comment> ***  Part Image  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnDir)">
			<xsl:choose>
				<xsl:when test="pnDir='pnDir'">
					<th class="unit">Image</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit center">
						<div>
							<xsl:attribute name="class">
								icon rotation<xsl:value-of select="(pnDir + PartDirOffset) mod 4"/>
							</xsl:attribute>
							<img class="icon">
								<xsl:attribute name="src">
									../../img/ShapeVT<xsl:value-of select="ImageVsnType"/>.bmp
								</xsl:attribute>
							</img>
						</div>
					</td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<!--
<xsl:comment> ***  Part Image 2  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnDir)">
			<xsl:choose>
				<xsl:when test="pnDir='pnDir'">
					<th class="unit">Image 2</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit">
						<div class="icon">
							<xsl:attribute name="style">
							<xsl:comment>PartDirOffsetだけ角度オフセットした後、BodyXMag,BodyYMagで画像を伸縮、さらにpnDir分だけ画像を回す</xsl:comment>
							filter:
								progid:DXImageTransform.Microsoft.BasicImage(rotation=<xsl:value-of select="(4 - PartDirOffset) mod 4"/>)
								progid:DXImageTransform.Microsoft.Matrix(M11=<xsl:value-of select="BodyXMag"/>,M22=<xsl:value-of select="BodyYMag"/>,M12=0.0,M21=0.0,SizingMethod="auto expand")
								progid:DXImageTransform.Microsoft.BasicImage(rotation=<xsl:value-of select="(4 - pnDir) mod 4"/>)
							</xsl:attribute>
							<img class="icon">
								<xsl:attribute name="src">
									../../VT<xsl:value-of select="ImageVsnType"/>_2.bmp
								</xsl:attribute>
							</img>
						</div>
					</td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>
-->

<xsl:comment> ***  Part Comment  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnPartComment)">
			<xsl:choose>
				<xsl:when test="pnPartComment='pnPartComment'">
					<th class="unit">Part Comment</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="pnPartComment"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Barcode Label  *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnBarcode)">
			<xsl:choose>
				<xsl:when test="pnBarcode='pnBarcode'">
					<th class="unit">Barcode Label</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="pnBarcode"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  Reference *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//fsRefList)">
			<xsl:choose>
				<xsl:when test="fsRefList='fsRefList'">
					<th class="unit">Reference</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="fsRefList"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  User Field 1 *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnUserField1)">
			<xsl:choose>
				<xsl:when test="pnUserField1='pnUserField1'">
					<th class="unit">User Field 1</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="pnUserField1"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  User Field 2 *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnUserField2)">
			<xsl:choose>
				<xsl:when test="pnUserField2='pnUserField2'">
					<th class="unit">User Field 2</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="pnUserField2"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  User Field 3 *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnUserField3)">
			<xsl:choose>
				<xsl:when test="pnUserField3='pnUserField3'">
					<th class="unit">User Field 3</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="pnUserField3"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  User Field 4 *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnUserField4)">
			<xsl:choose>
				<xsl:when test="pnUserField4='pnUserField4'">
					<th class="unit">User Field 4</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="pnUserField4"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

<xsl:comment> ***  User Field 5 *** </xsl:comment>
	<xsl:choose>
		<xsl:when test="count(//pnUserField5)">
			<xsl:choose>
				<xsl:when test="pnUserField5='pnUserField5'">
					<th class="unit">User Field 5</th>
				</xsl:when>
				<xsl:otherwise>
					<td class="unit"><xsl:value-of select="pnUserField5"/></td>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
		</xsl:otherwise>
	</xsl:choose>

</tr>
</xsl:template>
</xsl:stylesheet>
