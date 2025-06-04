# 🌦️ Projeto Clima - Case de Engenharia de Dados

Este projeto foi desenvolvido para demonstrar um pipeline de dados em streaming. O objetivo é demonstrar uma arquitetura moderna de ingestão, tratamento, organização e disponibilização de dados meteorológicos e de qualidade do ar utilizando recursos da **Microsoft Azure** e ferramentas de análise em tempo real.

---

## 🚀 Objetivo

Criar um pipeline completo de dados para coletar, tratar, enriquecer, analisar e disponibilizar informações climáticas, como:
- Temperatura atual e previsão para os próximos dias
- Condição do tempo traduzida para português
- Índices de qualidade do ar (CO, PM2.5)
- Visibilidade, pressão, vento e umidade

---

## 🏗️ Arquitetura

O pipeline é composto por diversas etapas e camadas:

### 🔹 Ingestão de Dados (Camada Bronze)
- **Azure Function** com Timer Trigger coleta dados da API do [WeatherAPI](https://www.weatherapi.com/) a cada 30 segundos.
- Dados são enviados para o **Event Hub** com autenticação via **Azure Key Vault**.
- O **Microsoft Fabric Eventstream** consome os dados e armazena no **Eventhouse** (KQL Database).

### 🔸 Transformação (Camada Silver)
- Função `transform_clima_silver()` em KQL:
  - Realiza join com dicionário de traduções de condições meteorológicas.
  - Normaliza e estrutura os dados.
  - Converte os campos e extrai previsões de temperatura dos dias seguintes.

### 🟡 Agregações (Camada Gold)
Diversas views analíticas foram criadas para exploração de dados:

- `gold_clima_atual`: Última medição por cidade
- `gold_previsao_temperatura`: Temperaturas previstas para os próximos dois dias
- `gold_ranking_poluição`: Ranking das cidades com maior poluição por PM2.5
- `gold_clima_por_estado`: Agregação da condição climática por estado
- `gold_previsao_temperatura_regiao`: Previsão de temperatura agrupada por região

---

## 📊 Visualização

- Os dados da camada Gold são conectados diretamente ao **Power BI**, possibilitando dashboards com insights climáticos por localização e previsão futura.

---

## ⚙️ Tecnologias Utilizadas

- **Azure Function (Python)**  
- **Azure Event Hub**  
- **Azure Key Vault**  
- **Microsoft Fabric (Eventstream, Eventhouse)**  
- **KQL (Kusto Query Language)**  
- **Power BI**  

---

## ✅ Boas práticas aplicadas

- Funções reutilizáveis
- Padronização de nomenclatura
- Enriquecimento e tradução de dados
- Camadas bronze, silver e gold bem definidas
- Planejamento para reprodutibilidade do projeto via script `.sh` no Azure Cloud Shell

---

## 💡 Considerações Finais

Este projeto demonstra o uso das ferramentas Azure e também boas práticas de engenharia de dados, como ingestão em tempo real, separação em camadas de tratamento e foco em insights de negócio com dashboards. O case é um exemplo completo e funcional de como construir um pipeline de dados moderno e escalável.

---

