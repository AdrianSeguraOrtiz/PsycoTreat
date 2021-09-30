<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
  <html>
    <body>
      <h1>Pacientes con sus formularios y pruebas complementarias clasificados por patología:</h1>
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
          <xsl:if test = "patologias_previas">
            <li><h3>Patologías Previas</h3></li>
            <ul>
            <xsl:for-each select = "patologias_previas/item">
              <li><h4><xsl:value-of select = "patologia"/></h4></li>
              <p></p>
              <table border = "1">
                <tr bgcolor="#81fa81">
                    <th>Patología</th>
                    <th>Fecha Inicio</th>
                    <th>Fecha Final</th>
                    <xsl:if test = "medicamentos_asignados">
                      <th>Medicamentos Asignados</th>
                    </xsl:if>
                </tr>
                <tr>
                    <td><xsl:value-of select = "patologia"/></td>
                    <td><xsl:value-of select = "fecha_inicio"/></td>
                    <td><xsl:value-of select = "fecha_final"/></td>
                    <xsl:if test = "medicamentos_asignados">
                    <td><ul>
                      <xsl:for-each select = "medicamentos_asignados/item">
                        <li><xsl:value-of select = "medicamento"/></li>
                      </xsl:for-each>
                      </ul></td>
                    </xsl:if>
                </tr>
              </table>
              <ul>
              <li><h4>Formularios</h4></li>
              <table border = "1">
                <tr bgcolor="#f7f26b">
                    <th>Fecha</th>
                    <th>Motivo Consulta</th>
                    <th>Desencadenante</th>
                    <th>Observaciones</th>
                    <th>Diagnóstico</th>
                    <th>Tratamiento</th>
                    <th>Frecuencia del tratamiento</th>
                </tr>
                <xsl:for-each select = "formularios_consultas/item">
                  <xsl:variable name="formulario" select="formulario"/>
                  <xsl:for-each select = "../../../../formularios_previos/item">
                    <xsl:if test = "$formulario = _id"> 
                      <tr>
                          <td><xsl:value-of select = "fecha_consulta"/></td>
                          <td><xsl:value-of select = "motivo_consulta"/></td>
                          <td><xsl:value-of select = "desencadenante"/></td>
                          <td><xsl:value-of select = "observaciones"/></td>
                          <td><xsl:value-of select = "diagnostico"/></td>
                          <td><xsl:value-of select = "tratamiento"/></td>
                          <td><xsl:value-of select = "frecuencia_tratamiento"/></td>
                      </tr>
                    </xsl:if>
                  </xsl:for-each>
                </xsl:for-each>
              </table>
              <p></p>
              <xsl:if test = "pruebas_complementarias">
                <li><h4>Pruebas Complementarias</h4></li>
                <table border = "1">
                  <tr bgcolor="#62fcf9">
                    <th>Prueba</th>
                  </tr>
                  <tr>
                    <xsl:for-each select="pruebas_complementarias/item">
                      <td><xsl:value-of select = "prueba"/></td>
                    </xsl:for-each>
                  </tr>
                </table>
                <p></p>
              </xsl:if>
              </ul>
            </xsl:for-each>
            </ul>
          </xsl:if>
          <xsl:if test = "patologia_actual">
            <li><h3>Patología Actual:&#160;<xsl:value-of select = "patologia_actual"/></h3></li>
            <p></p>
            <table border = "1">
              <tr bgcolor="#81fa81">
                  <th>Patología</th>
                  <th>Fecha Inicio</th>
                  <xsl:if test = "medicamentos_asignados">
                    <th>Medicamentos Asignados</th>
                  </xsl:if>
              </tr>
              <tr>
                  <td><xsl:value-of select = "patologia_actual"/></td>
                  <td><xsl:value-of select = "fecha_inicio"/></td>
                  <xsl:if test = "medicamentos_asignados">
                  <td><ul>
                    <xsl:for-each select = "medicamentos_asignados/item">
                      <li><xsl:value-of select = "medicamento"/></li>
                    </xsl:for-each>
                    </ul></td>
                  </xsl:if>
              </tr>
            </table>
            <ul>
            <li><h4>Formularios</h4></li>
            <table border = "1">
              <tr bgcolor="#f7f26b">
                  <th>Fecha</th>
                  <th>Motivo Consulta</th>
                  <th>Desencadenante</th>
                  <th>Observaciones</th>
                  <th>Diagnóstico</th>
                  <th>Tratamiento</th>
                  <th>Frecuencia del tratamiento</th>
              </tr>
              <xsl:for-each select = "formularios_consultas/item">
                <xsl:variable name="formulario" select="formulario" />
                <xsl:for-each select = "../../formularios_actuales/item">
                  <xsl:if test = "$formulario = _id"> 
                    <tr>
                        <td><xsl:value-of select = "fecha_consulta"/></td>
                        <td><xsl:value-of select = "motivo_consulta"/></td>
                        <td><xsl:value-of select = "desencadenante"/></td>
                        <td><xsl:value-of select = "observaciones"/></td>
                        <td><xsl:value-of select = "diagnostico"/></td>
                        <td><xsl:value-of select = "tratamiento"/></td>
                        <td><xsl:value-of select = "frecuencia_tratamiento"/></td>
                    </tr>
                  </xsl:if>
                </xsl:for-each>
              </xsl:for-each>
            </table>
            <p></p>
            <xsl:if test = "pruebas_complementarias">
              <li><h4>Pruebas Complementarias</h4></li>
              <table border = "1">
                <tr bgcolor="#62fcf9">
                  <th>Prueba</th>
                </tr>
                <tr>
                  <xsl:for-each select="pruebas_complementarias/item">
                    <td><xsl:value-of select = "prueba"/></td>
                  </xsl:for-each>
                </tr>
              </table>
              <p></p>
            </xsl:if>
            </ul>
          </xsl:if>
        </ul>
      </xsl:for-each>
      </ul>
    </body>
  </html>
</xsl:template>
</xsl:stylesheet>