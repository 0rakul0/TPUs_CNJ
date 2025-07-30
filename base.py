import pandas as pd
import glob
import os
import re

def gerador(tag):
    DIR = f'./LAKE/{tag}/*.xlsx'
    os.makedirs(f'./OUTPUT/{tag}')
    arq = glob.glob(DIR)

    dfs = []


    for a in arq:
        df = pd.read_excel(a)

        df["nome"] = df.iloc[:, :5].apply(lambda x: "".join(x.dropna().astype(str)), axis=1)

        df.drop(df.columns[:5], axis=1, inplace=True)

        df["Código"] = df["Código"].astype('Int64')
        df["Cód. Pai"] = df["Cód. Pai"].astype('Int64')

        df = df[["Código",'Cód. Pai',"nome"]]

        df = df.dropna(subset='Código')

        nome_arquivo = os.path.basename(a).replace(".xlsx", "")

        marcador = "".join(re.findall(r"[A-Z1-2]", nome_arquivo))

        df[marcador] = "X"

        df.to_csv(f'./OUTPUT/{tag}/{tag}_{marcador}.csv', index=False)


    # Listar todos os CSVs criados
    csv_files = glob.glob(f"./OUTPUT/{tag}/*.csv")

    # Inicializar df_final como None para primeira iteração
    df_final = None

    def ajustar_tipo_codigo(df):
        for col in ["Código", "Cód. Pai"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)  # Remover ".0"
                df[col] = df[col].replace("nan", "")  # Converter NaN para string vazia
        return df

    # Carregar e mesclar cada CSV
    for file in csv_files:
        df_temp = pd.read_csv(file)
        try:
            df_temp["Código"] = df_temp["Código"].astype('Int64')
            df_temp["Cód. Pai"] = df_temp["Cód. Pai"].astype('Int64')

            df_temp = df_temp.dropna(subset='Código')

            if df_final is None:
                df_final = df_temp
            else:
                df_final = pd.merge(df_final, df_temp, on=["Código",'Cód. Pai',"nome"], how="outer")

                df_final = df_final.drop_duplicates()
        except Exception as e:
            print(file, '\n\n', e)


    def formatar_nome_coluna(coluna):
        coluna = coluna.lower()  # Converter para minúsculas
        coluna = re.sub(r'[^a-z0-9\s]', '', coluna)  # Remover caracteres especiais
        coluna = coluna.replace(" ", "_")  # Substituir espaços por _
        return coluna

    # Dicionário de renomeação específico
    renomeacao = {
        "código": "id",
        "cód_pai": "id_pai"
    }

    colunas_originais = ["nome", "Código", "Cód. Pai"]

    renomeacao_geral = {col: formatar_nome_coluna(col) for col in colunas_originais}

    renomeacao_geral.update(renomeacao)

    df_final = df_final.rename(columns=renomeacao_geral)

    df_final.to_csv(f'./BANCO/{tag}_tpu_nome_marcadores.csv', index=False)

tag = ['Assunto', 'Movimentos', 'classe']
for i in tag:
    gerador(i)