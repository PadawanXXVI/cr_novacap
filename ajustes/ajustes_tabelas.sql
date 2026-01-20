use cr_novacap;

select * from demandas;

ALTER TABLE demandas
  ADD COLUMN ativo TINYINT(1) NOT NULL DEFAULT 1,
  ADD COLUMN versao_catalogo VARCHAR(10) NOT NULL DEFAULT 'V1',
  ADD COLUMN substitui_id_demanda INT NULL;
  
  DESCRIBE demandas;
  
  SELECT versao_catalogo, ativo, COUNT(*) AS qtd
FROM demandas
GROUP BY versao_catalogo, ativo
ORDER BY versao_catalogo, ativo;

START TRANSACTION;

INSERT INTO demandas (descricao, ativo, versao_catalogo)
SELECT v.descricao, 1, 'V2'
FROM (
    SELECT 'Alambrado (Cercamento) - Implantação' AS descricao
    UNION ALL SELECT 'Alambrado (Cercamento) - Reparos'

    UNION ALL SELECT 'Boca de Lobo - Desobstrução'
    UNION ALL SELECT 'Boca de Lobo - Implantação'
    UNION ALL SELECT 'Boca de Lobo - Limpeza'
    UNION ALL SELECT 'Boca de Lobo - Reparos'
    UNION ALL SELECT 'Boca de Lobo - Reposição de Grelha/Grades'
    UNION ALL SELECT 'Boca de Lobo - Reposição de Tampa'

    UNION ALL SELECT 'Bueiro - Desobstrução'
    UNION ALL SELECT 'Bueiro - Implantação'
    UNION ALL SELECT 'Bueiro - Limpeza'
    UNION ALL SELECT 'Bueiro - Reparos'
    UNION ALL SELECT 'Bueiro - Reposição de Grelha/Grade'
    UNION ALL SELECT 'Bueiro - Reposição de Tampa'

    UNION ALL SELECT 'Calçada - Implantação'
    UNION ALL SELECT 'Calçada - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Calçada - Reparos'
    UNION ALL SELECT 'Calçada - Sinalização Horizontal'

    UNION ALL SELECT 'Ciclovia ou Ciclofaixa (Pista)'

    UNION ALL SELECT 'Doação de Mudas'

    UNION ALL SELECT 'Estacionamentos - Implantação'
    UNION ALL SELECT 'Estacionamentos - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Estacionamentos - Reparos'
    UNION ALL SELECT 'Estacionamentos - Sinalização Horizontal (Implantação)'
    UNION ALL SELECT 'Estacionamentos - Sinalização Horizontal (Revitalização)'
    UNION ALL SELECT 'Estacionamentos - Tapa-Buraco'
    UNION ALL SELECT 'Estacionamentos - Vagas Especiais'

    UNION ALL SELECT 'Galeria de Águas Pluviais - Desobstrução'
    UNION ALL SELECT 'Galeria de Águas Pluviais - Implantação'
    UNION ALL SELECT 'Galeria de Águas Pluviais - Limpeza'
    UNION ALL SELECT 'Galeria de Águas Pluviais - Reparos'
    UNION ALL SELECT 'Galeria de Águas Pluviais - Reposição de Grelha/Grade'
    UNION ALL SELECT 'Galeria de Águas Pluviais - Reposição de Tampa'

    UNION ALL SELECT 'Jardim - Implantação'
    UNION ALL SELECT 'Jardim - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Jardim - Revitalização'
    UNION ALL SELECT 'Jardim - Roçagem'

    UNION ALL SELECT 'Limpeza de Resíduos de Obras da Novacap'

    UNION ALL SELECT 'Meio-fio - Capina e Pintura'
    UNION ALL SELECT 'Meio-fio - Implantação'
    UNION ALL SELECT 'Meio-fio - Pintura'
    UNION ALL SELECT 'Meio-fio - Reparos'

    UNION ALL SELECT 'Parceria - Fornecimento de Massa Asfáltica (Tapa-Buraco)'
    UNION ALL SELECT 'Parceria - Fornecimento de Materiais/Insumos (areia, brita, meio-fio etc.)'
    UNION ALL SELECT 'Parceria - Solicitação de Máquinas, Veículos ou Equipamentos'

    UNION ALL SELECT 'Parque Infantil - Implantação'
    UNION ALL SELECT 'Parque Infantil - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Parque Infantil - Limpeza'
    UNION ALL SELECT 'Parque Infantil - Reparo nos Brinquedos'
    UNION ALL SELECT 'Parque Infantil - Reparos Diversos'
    UNION ALL SELECT 'Parque Infantil - Roçagem'

    UNION ALL SELECT 'Passagem Subterrânea - Implantação'
    UNION ALL SELECT 'Passagem Subterrânea - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Passagem Subterrânea - Limpeza'
    UNION ALL SELECT 'Passagem Subterrânea - Reparos Diversos'

    UNION ALL SELECT 'Passarela - Implantação'
    UNION ALL SELECT 'Passarela - Limpeza'
    UNION ALL SELECT 'Passarela - Reparos Diversos'

    UNION ALL SELECT 'Pisos Articulados - Implantação'
    UNION ALL SELECT 'Pisos Articulados - Reparos'

    UNION ALL SELECT 'Pista de Skate - Implantação'
    UNION ALL SELECT 'Pista de Skate - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Pista de Skate - Pintura'
    UNION ALL SELECT 'Pista de Skate - Reparo do Piso'
    UNION ALL SELECT 'Pista de Skate - Reparos Diversos'
    UNION ALL SELECT 'Pista de Skate - Roçagem'

    UNION ALL SELECT 'Poda de Árvore'
    UNION ALL SELECT 'Poda de Árvore - Coleta de Galhos e Troncos'
    UNION ALL SELECT 'Poda de Árvore - Corte (Erradicação)'
    UNION ALL SELECT 'Poda de Árvore - Retirada de Árvore Morta ou Caída'

    UNION ALL SELECT 'Ponto de Encontro Comunitário (PEC) - Implantação'
    UNION ALL SELECT 'Ponto de Encontro Comunitário (PEC) - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Ponto de Encontro Comunitário (PEC) - Limpeza'
    UNION ALL SELECT 'Ponto de Encontro Comunitário (PEC) - Reparo dos Equipamentos'
    UNION ALL SELECT 'Ponto de Encontro Comunitário (PEC) - Reparos Diversos'
    UNION ALL SELECT 'Ponto de Encontro Comunitário (PEC) - Roçagem'

    UNION ALL SELECT 'Praça - Implantação'
    UNION ALL SELECT 'Praça - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Praça - Limpeza'
    UNION ALL SELECT 'Praça - Revitalização'
    UNION ALL SELECT 'Praça - Roçagem'

    UNION ALL SELECT 'Quadra de Esporte - Implantação'
    UNION ALL SELECT 'Quadra de Esporte - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Quadra de Esporte - Limpeza'
    UNION ALL SELECT 'Quadra de Esporte - Revitalização'
    UNION ALL SELECT 'Quadra de Esporte - Roçagem'

    UNION ALL SELECT 'Rampa - Implantação'
    UNION ALL SELECT 'Rampa - Reparo'
    UNION ALL SELECT 'Rampa - Sinalização'

    UNION ALL SELECT 'Roçagem'

    UNION ALL SELECT 'Rua, Via ou Rodovia (Pista) - Alargamento'
    UNION ALL SELECT 'Rua, Via ou Rodovia (Pista) - Implantação'
    UNION ALL SELECT 'Rua, Via ou Rodovia (Pista) - Implantação de Placa de Sinalização'
    UNION ALL SELECT 'Rua, Via ou Rodovia (Pista) - Recuperação / Melhorias'
    UNION ALL SELECT 'Rua, Via ou Rodovia (Pista) - Roçagem'
    UNION ALL SELECT 'Rua, Via ou Rodovia (Pista) - Sinalização Horizontal'
    
    UNION ALL SELECT 'Tapa-Buraco - Revitalização'
) AS v
LEFT JOIN demandas d
  ON d.descricao = v.descricao
 AND d.versao_catalogo = 'V2'
WHERE d.id_demanda IS NULL;

COMMIT;

SELECT versao_catalogo, ativo, COUNT(*) AS qtd
FROM demandas
GROUP BY versao_catalogo, ativo
ORDER BY versao_catalogo, ativo;

SELECT descricao, COUNT(*) AS qtd
FROM demandas
WHERE versao_catalogo = 'V2'
GROUP BY descricao
HAVING COUNT(*) > 1;

ALTER TABLE diretorias
  ADD COLUMN tipo VARCHAR(12) NOT NULL DEFAULT 'INTERNA',
  ADD COLUMN ativo TINYINT(1) NOT NULL DEFAULT 1,
  ADD COLUMN ordem_exibicao INT NOT NULL DEFAULT 0;
  
  SELECT * FROM diretorias;
  
START TRANSACTION;

SHOW CREATE TABLE diretorias;
SHOW FULL COLUMNS FROM diretorias;

SELECT * FROM diretorias ORDER BY id_diretoria;

UPDATE diretorias
SET ativo = 1
WHERE ativo IS NULL;

-- Diretorias internas
UPDATE diretorias
SET tipo = 'INTERNA'
WHERE sigla IN ('DC','DO','DP','DS','DJ');

-- Externa (não tramita)
UPDATE diretorias
SET tipo = 'EXTERNA'
WHERE sigla = 'EXT';

-- Sistemas
UPDATE diretorias
SET tipo = 'SISTEMA'
WHERE sigla IN ('SGIA','SCTB');

INSERT INTO diretorias (nome_completo, sigla, tipo, ativo, ordem_exibicao)
SELECT 'Diretoria Jurídica', 'DJ', 'INTERNA', 1, 5
WHERE NOT EXISTS (
    SELECT 1 FROM diretorias WHERE sigla = 'DJ'
);

INSERT INTO diretorias (nome_completo, sigla, tipo, ativo, ordem_exibicao)
SELECT 'Tramita via SCTB', 'SCTB', 'SISTEMA', 1, 91
WHERE NOT EXISTS (
    SELECT 1 FROM diretorias WHERE sigla = 'SCTB'
);

UPDATE diretorias SET ordem_exibicao = 1  WHERE sigla = 'DC';
UPDATE diretorias SET ordem_exibicao = 2  WHERE sigla = 'DO';
UPDATE diretorias SET ordem_exibicao = 3  WHERE sigla = 'DP';
UPDATE diretorias SET ordem_exibicao = 4  WHERE sigla = 'DS';
UPDATE diretorias SET ordem_exibicao = 5  WHERE sigla = 'DJ';

UPDATE diretorias SET ordem_exibicao = 90 WHERE sigla = 'SGIA';
UPDATE diretorias SET ordem_exibicao = 91 WHERE sigla = 'SCTB';
UPDATE diretorias SET ordem_exibicao = 99 WHERE sigla = 'EXT';

SELECT
  ordem_exibicao,
  sigla,
  descricao_exibicao,
  tipo
FROM diretorias
ORDER BY ordem_exibicao;

SELECT * FROM regioes_administrativas;

INSERT INTO departamentos (nome, id_diretoria)
SELECT x.nome, d.id_diretoria
FROM (
    SELECT 'Departamento Jurídico Civil (DJC)'        AS nome
    UNION ALL
    SELECT 'Departamento Jurídico Consultivo (DCO)'
    UNION ALL
    SELECT 'Departamento Jurídico Preventivo (DJP)'
    UNION ALL
    SELECT 'Departamento Jurídico Trabalhista (DJT)'
) x
JOIN diretorias d
  ON d.sigla = 'DJ'
LEFT JOIN departamentos dp
  ON dp.nome = x.nome
WHERE dp.id_departamento IS NULL;

select * from status;

USE cr_novacap;

/* 0) Snapshot rápido (antes) */
SELECT id_status, descricao, ordem_exibicao, finaliza_processo
FROM status
ORDER BY id_status;

SELECT COUNT(*) AS total_status FROM status;

/* 1) Garantir consistência mínima (evitar NULL em flags) */
UPDATE status
SET finaliza_processo = 0
WHERE finaliza_processo IS NULL;

/* 2) Inserir NOVOS STATUS (somente se não existirem) */
START TRANSACTION;

-- 2.1) Improcedente – tramitação via SCTB
INSERT INTO status (descricao, ordem_exibicao, finaliza_processo)
SELECT 'Improcedente – tramitação via SCTB', 0, 0
WHERE NOT EXISTS (
  SELECT 1 FROM status WHERE descricao = 'Improcedente – tramitação via SCTB'
);

-- 2.2) Devolvido à RA de origem – parceria (fornecimento de recursos pela NOVACAP)
INSERT INTO status (descricao, ordem_exibicao, finaliza_processo)
SELECT 'Devolvido à RA de origem – parceria (fornecimento de recursos pela NOVACAP)', 0, 0
WHERE NOT EXISTS (
  SELECT 1 FROM status
  WHERE descricao = 'Devolvido à RA de origem – parceria (fornecimento de recursos pela NOVACAP)'
);

-- 2.3) Devolvido à RA de origem – solicitação de fonte orçamentária
INSERT INTO status (descricao, ordem_exibicao, finaliza_processo)
SELECT 'Devolvido à RA de origem – solicitação de fonte orçamentária', 0, 0
WHERE NOT EXISTS (
  SELECT 1 FROM status
  WHERE descricao = 'Devolvido à RA de origem – solicitação de fonte orçamentária'
);

COMMIT;

/* 3) Checar duplicidades por descricao (precisa voltar vazio) */
SELECT descricao, COUNT(*) AS qtd
FROM status
GROUP BY descricao
HAVING COUNT(*) > 1;

/* 4) (OPCIONAL, RECOMENDADO) Blindar contra duplicidade futura
      Só execute se o SELECT acima vier vazio.
*/
-- ALTER TABLE status
-- ADD UNIQUE KEY uq_status_descricao (descricao);

/* 5) Recalcular ordem_exibicao em ORDEM ALFABÉTICA (A-Z) pela descricao
      Mantém IDs intactos; só define a ordem de exibição.
*/
WITH ranked AS (
  SELECT
    id_status,
    ROW_NUMBER() OVER (ORDER BY descricao ASC) AS nova_ordem
  FROM status
)
UPDATE status s
JOIN ranked r ON r.id_status = s.id_status
SET s.ordem_exibicao = r.nova_ordem;

/* 6) Resultado final (depois) */
SELECT ordem_exibicao, id_status, descricao, finaliza_processo
FROM status
ORDER BY ordem_exibicao;

SELECT COUNT(*) AS total_status_final FROM status;