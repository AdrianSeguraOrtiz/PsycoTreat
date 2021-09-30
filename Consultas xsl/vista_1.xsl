<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
  <html>
    <body>
        <h1>Psiquiatras y sus pacientes:</h1>
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
                    <li><h3>Información profesional</h3></li>
                    <table border = "1">
                        <tr bgcolor="#81fa81">
                            <th>Titulación</th>
                            <th>Universidad</th>
                            <th>Especialidad</th>
                            <th>Años de antiguedad en el centro</th>
                            <th>Número de pacientes</th>
                        </tr>
                        <tr>
                            <td><xsl:value-of select = "titulacion"/></td>
                            <td><xsl:value-of select = "universidad"/></td>
                            <td><xsl:value-of select = "especialidad"/></td>
                            <td><xsl:value-of select = "años_antiguedad_en_centro"/></td>
                            <td><xsl:value-of select = "numero_de_pacientes"/></td>
                        </tr>
                    </table>
                    <p></p>
                    <li><h3>Antiguos pacientes</h3></li>
                    <xsl:variable name="id_psiquiatra" select="_id"/>
                    <table border = "1">
                        <tr bgcolor="#f7f26b">
                            <th>Nombre</th>
                            <th>Apellidos</th>
                            <th>DNI</th>
                            <th>Patología: Fecha</th>
                        </tr>
                        <xsl:for-each select = "pacientes_antiguos/item">
                            <tr>
                                <td><xsl:value-of select = "nombre"/></td>
                                <td><xsl:value-of select = "apellidos"/></td>
                                <td><xsl:value-of select = "dni"/></td>
                                <td><ul>
                                    <xsl:for-each select = "patologias_previas/item">
                                        <xsl:if test = "psiquiatra_asignado = $id_psiquiatra">
                                            <li><xsl:value-of select = "patologia"/>: <xsl:value-of select = "fecha_inicio"/>-<xsl:value-of select = "fecha_final"/></li>
                                        </xsl:if>
                                    </xsl:for-each>
                                </ul></td>
                            </tr>
                        </xsl:for-each>
                    </table>
                    <li><h3>Pacientes actuales en tratamiento</h3></li>
                    <table border = "1">
                        <tr bgcolor="#62fcf9">
                            <th>Nombre</th>
                            <th>Apellidos</th>
                            <th>DNI</th>
                            <th>Patología</th>
                            <th>Fecha Inicio</th>
                        </tr>
                        <xsl:for-each select = "pacientes_actuales/item">
                            <tr>
                                <td><xsl:value-of select = "nombre"/></td>
                                <td><xsl:value-of select = "apellidos"/></td>
                                <td><xsl:value-of select = "dni"/></td>
                                <td><xsl:value-of select = "patologia_actual"/></td>
                                <td><xsl:value-of select = "fecha_inicio"/></td>
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