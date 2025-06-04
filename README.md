| Resumo do Case
Este projeto tem como objetivo demonstrar a construção de um pipeline completo de ingestão, transformação e visualização de dados em tempo real utilizando os recursos do Microsoft Fabric e serviços da Azure.
A ingestão começa com uma Azure Function configurada com um Timer Trigger, que consome dados meteorológicos de uma API externa. A autenticação é feita por meio de um Service Principal Name (SPN) com credenciais armazenadas no Azure Key Vault, garantindo segurança.
