<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
  <html>
    <body>
        <h1>Informe enfermedades mentales:</h1>
        <table border = "1">
            <tr bgcolor="#ff6d6d">
                <th>Enfermedad Mental</th>
                <th>Total de casos</th>
            </tr>
            <xsl:for-each select="all/item">
                <tr>
                    <td><xsl:value-of select = "enfermedad"/></td>
                    <td><xsl:value-of select = "total"/></td>
                </tr>
            </xsl:for-each>
        </table>
    </body>
  </html>
</xsl:template>
</xsl:stylesheet>