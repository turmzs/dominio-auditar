# TODO - Motor Fiscal e Módulo de Escrita Fiscal (Domínio Auditar)

## Próximos passos (do fluxo 1 ao 5)

- [ ] 1) Definir contrato canônico de evento/item para o engine (CST/CSOSN, CFOP, UF, bases e valores por imposto).
- [ ] 2) Especificar camadas do módulo:
  - [ ] Capture (Importação XML/NF-e/NFS-e/CT-e, Sieg etc.)
  - [ ] Parametrização/Config Fiscal (Acumuladores, vigência, alíquotas, ST/MVA)
  - [ ] Core (apuração, DIFAL, CIAP, ajustes, retenções)
  - [ ] Output (guias, livros fiscais, relatórios de conferência)
  - [ ] Compliance (SPEDs, EFD-Reinf, declarações estaduais/municipais, DCTFWeb/e-CAC)
- [ ] 3) Propor e implementar (v2) `RulesEngine` por regras versãoadas (router + evaluator + ledger + guide generator) sem quebrar API atual.
- [ ] 4) Criar `TaxLedger` e modelo de conferência (trace detalhado por regra aplicada).
- [ ] 5) Ajustar endpoints de apuração para consumir o ledger em vez do motor estimado.

## Reforma Tributária (novo cenário) depois do 1-5

- [ ] 6) Implementar Apuração Dual (IBS/CBS) com “princípio do destino”.
- [ ] 7) Implementar Split Payment (retenção e recolhimento na liquidação).

## Regimes especiais e nichos depois do 1-5

- [ ] 8) RECOF / RECOF-SPED
- [ ] 9) Apuração de combustíveis (ANP)
- [ ] 10) Crédito presumido de transportes

## Auditoria e inteligência depois do 1-5

- [ ] 11) Pre-validation SPED
- [ ] 12) Cruzamento EFD vs XML
- [ ] 13) Ressarcimento/complemento ICMS-ST

## Gestão patrimonial depois do 1-5

- [ ] 14) FCI
- [ ] 15) e-CredAc (créditos acumulados)

## Integração Thomson Reuters depois do 1-5

- [ ] 16) Integração módulo patrimônio (Ativo Imobilizado/CIAP)
- [ ] 17) Exportação contábil (lançamentos DRE/Balanço)
