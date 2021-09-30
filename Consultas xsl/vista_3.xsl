<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
  <html>
    <body>
        <h1>Familiares de pacientes y sus mensajes:</h1>
        <ul>
            <xsl:for-each select = "all/item">
                <li><h2><xsl:value-of select = "nombre"/>&#160;<xsl:value-of select = "apellidos"/></h2></li>
                <ul>
                    <li><h3>Información personal</h3></li>
                    <table border = "1">
                        <tr bgcolor="#ff6d6d">
                            <th>Nombre</th>
                            <th>Apellidos</th>
                            <th>DNI</th>
                            <th>Fecha de Nacimiento</th>
                            <th>Sexo</th>
                            <th>Email</th>
                            <th>Teléfono</th>
                        </tr>
                        <tr>
                            <td><xsl:value-of select = "nombre"/></td>
                            <td><xsl:value-of select = "apellidos"/></td>
                            <td><xsl:value-of select = "dni"/></td>
                            <td><xsl:value-of select = "fecha_de_nacimiento"/></td>
                            <td><xsl:value-of select = "sexo"/></td>
                            <td><xsl:value-of select = "email"/></td>
                            <td><xsl:value-of select = "telefono"/></td>
                        </tr>
                    </table>
                    <p></p>
                    <li><h3>Relación con paciente</h3></li>
                    <table border = "1">
                        <tr bgcolor="#81fa81">
                            <th rowspan = "2">Relación</th>
                            <th colspan = "4">Paciente asociado</th>
                            <th rowspan = "2">Nivel de autorización</th>
                        </tr>
                        <tr bgcolor="#81fa81">
                            <th>Nombre</th>
                            <th>Apellidos</th>
                            <th>DNI</th>
                            <th>Fecha de Nacimiento</th>
                        </tr>
                        <tr>
                            <td><xsl:value-of select = "relacion"/></td>
                            <td><xsl:value-of select = "paciente_asociado/item/nombre"/></td>
                            <td><xsl:value-of select = "paciente_asociado/item/apellidos"/></td>
                            <td><xsl:value-of select = "paciente_asociado/item/dni"/></td>
                            <td><xsl:value-of select = "paciente_asociado/item/fecha_de_nacimiento"/></td>
                            <td><xsl:value-of select = "nivel_de_autorizacion"/></td>
                        </tr>
                    </table>
                    <p></p>
                    <li><h3>Mensajes recibidos</h3></li>
                    <table border = "1">
                        <tr bgcolor="#f7f26b">
                            <th colspan = "3">Emisor</th>
                            <th rowspan = "2">Fecha</th>
                            <th rowspan = "2">Contenido</th>
                        </tr>
                        <tr bgcolor="#f7f26b">
                            <th>Nombre</th>
                            <th>Apellidos</th>
                            <th>Cargo en el centro</th>
                        </tr>
                        <xsl:for-each select = "mensajes_recibidos/item">
                            <xsl:variable name="id_emisor" select="emisor"/>
                            <tr>
                                <xsl:for-each select = "../../emisores/item">
                                    <xsl:if test = "_id = $id_emisor">
                                        <td><xsl:value-of select = "nombre"/></td>
                                        <td><xsl:value-of select = "apellidos"/></td>
                                        <td>Psiquiatra</td>
                                    </xsl:if>
                                </xsl:for-each>
                                <td><xsl:value-of select = "fecha_de_envio"/></td>
                                <td><xsl:value-of select = "contenido"/></td>
                            </tr>    
                        </xsl:for-each>
                    </table>
                </ul>
            </xsl:for-each>
        </ul>
    </body>
  </html>
</xsl:template>
</xsl:stylesheet>