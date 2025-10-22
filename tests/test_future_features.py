from __future__ import annotations

import pytest


@pytest.mark.xfail(reason="Aba de vagas ainda não foi implementada")
def test_navegacao_para_aba_de_vagas():
    raise NotImplementedError("Navegar para aba de vagas")


@pytest.mark.xfail(reason="Filtros avançados ainda não foram implementados")
def test_modificacao_de_filtros_de_pesquisa():
    raise NotImplementedError("Modificar filtros de pesquisa")


@pytest.mark.xfail(reason="Campo de pesquisa automatizado ainda não foi implementado")
def test_inserir_texto_no_campo_de_pesquisa():
    raise NotImplementedError("Inserir termo de pesquisa")


@pytest.mark.xfail(reason="Fluxo de candidatura automática ainda não foi implementado")
def test_aplicar_para_vaga():
    raise NotImplementedError("Aplicar para vaga")


@pytest.mark.xfail(reason="Carregamento do perfil ainda não foi implementado")
def test_carregar_perfil_usuario():
    raise NotImplementedError("Carregar perfil do usuário")


@pytest.mark.xfail(reason="Campos de experiência ainda não foram implementados")
def test_verificar_campos_experiencia():
    raise NotImplementedError("Verificar campos de experiências")


@pytest.mark.xfail(reason="Campos de formação acadêmica ainda não foram implementados")
def test_verificar_formacao_academica():
    raise NotImplementedError("Verificar formação acadêmica")


@pytest.mark.xfail(reason="Importação de PDF ainda não foi implementada")
def test_importacao_pdf():
    raise NotImplementedError("Importar currículo PDF")


@pytest.mark.xfail(reason="Importação de DOC ainda não foi implementada")
def test_importacao_doc():
    raise NotImplementedError("Importar currículo DOC")
