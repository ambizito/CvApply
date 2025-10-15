# Plano de Testes de Software

<span style="color:red">Pré-requisitos: <a href="2-Especificação do Projeto.md"> Especificação do Projeto</a></span>, <a href="3-Projeto de Interface.md"> Projeto de Interface</a>

 
8. Plano de Teste de Software
Requisitos para testes de software:
•	A aplicação deve possuir um tópico de dicas de como montar um CV.
•	A aplicação deve possuir layouts predefinidos e a opção de personalizar.
•	A aplicação deve ter página de fácil navegação, para facilitar correções, caso seja necessário.

Os testes funcionais a serem praticados no site são descritos a seguir.

| Caso de Teste| CT-01 - Montagem de CV| 
|--------------|-----------------------|
|Requisitos associados|  RF-03: A aplicação deve possuir um tópico de dicas de como montar um CV.|
|                    | RF-06: A aplicação deve possuir layouts predefinidos e a opção de personalizar.|
|Objetivo de teste|Conferir o acesso e a qualidade das informações disponibilizadas para a montagem de um CV.|
|Passos|1)	Acessar Home-Page.|
| |2)	Acessar a opção dicas na tela inicial e localizar a opção dicas e selecionar.|
| |3)	Acessar a opção layouts e selecionar a opção que mais se identifica com o usuário.|
|Critério de êxito|•	Ao acessar a página inicial você deve ser direcionado para a página de dicas para a leitura de informações essenciais para a construção do seu CV.|
| \•	Ao selecionar a opção de templates deve ser disponibilizados exemplos para o preenchimento dos seus dados.|


|Caso de teste| CT-02 – Navegabilidade|
|-------------|----------------------------------------------------------------|
|Requisitos Associados| RF-07 - A aplicação deve ter páginas de fácil navegação, para facilitar correções, caso seja necessário.|
|Objetivo do Teste| Pensado especialmente para pessoas que enfrentam dificuldades ao lidar com tarefas ou aplicações online.|
|Passos|1)	Acessar Home-Page.|
|  |2)	Selecionar abas Site e Dicas|
| |3)	Inserir dados.|
| |4)	Finalizar o CV.|
|Critérios de Êxito|•	Facilidade de navegação, voltar e avançar em qualquer aba sem a necessidade de voltar nas que foram acessadas.|
| |•	A aba 'Dicas' é uma ferramenta útil que oferece orientações claras e práticas para auxiliar na criação de um currículo.|

|Caso de teste| CT-03 – Responsividade|
|-------------|----------------------------------------------------------------|
|Requisitos Associados| RNF-009 A aplicação deve ser responsiva, para celulares e dispositivos móveis com fácil navegação, para facilitar correções caso seja necessário.|
|Objetivo do Teste| Pensado especialmente para pessoas que utilizam dispositivos móveis para a maioria das tarefas diárias.|
|Passos|1)	Acessar Home-Page.|
|  |2)	Selecionar abas Site e Dicas|
|  |3)	Inserir dados.|
| |4)	Finalizar o CV.|
|Critérios de Êxito|•	Aplicação é legível e editável e suas funções em qualquer tipo de aparelho.|
 
|Caso de teste| CT-04 – Envio por email|
|-------------|----------------------------------------------------------------|
|Requisitos Associados| RF-008 A aplicação deve ter a opção de envio do CV diretamente ao e-mail
|Objetivo do Teste| Acessar a funcionalidade de envio por email|
|Passos|1)	Acessar Home-Page.|
| |2)	Selecionar abas Site e Dicas|
| |3)	Inserir dados.|
| |4)	Finalizar o CV.|
|Critérios de Êxito|•	Aplicação deve enviar o currículo pronto para o email designado|

|Caso de teste| CT-05 – Salvar CV em formato PDF
|-------------|----------------------------------------------------------------|
|Requisitos Associados| RF-008 A aplicação deve ter a opção de salvar o CV em formato PDF
|Objetivo do Teste| Salvar o CV em formato PDF
|Passos|1)	Acessar Home-Page.|
| |2)	Selecionar abas Site e Dicas|
| |3)	Inserir dados.|
| |4)	Finalizar o CV.|
|Critérios de Êxito|•	Aplicação deve salvar o CV em formato PDF|

