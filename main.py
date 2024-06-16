# Projeto final da disciplina Linguagem de Programação
# Aluno: José Victor Silva Sousa


from fastapi import FastAPI, HTTPException
import json

app = FastAPI()

alunos = []

def carregar_dados():
    global alunos
    try:
        with open('alunos.json', 'r') as f:
            alunos = json.load(f)
    except FileNotFoundError:
        alunos = []
    except json.JSONDecodeError:
        alunos = []

def salvar_dados():
    with open('alunos.json', 'w') as f:
        json.dump(alunos, f)

@app.post("/adicionar_aluno/")
async def adicionar_aluno(aluno: dict):
    for disciplina in aluno['notas']:
        nota = aluno['notas'][disciplina]
        if nota < 0 or nota > 10:
            raise HTTPException(status_code=400, detail="Notas devem estar entre 0 e 10. Tente novamente!")
        aluno['notas'][disciplina] = round(nota, 1)

    for a in alunos:
        if a["id"] == aluno['id']:
            raise HTTPException(status_code=400, detail="ID do aluno já existe. Tente novamente!")
    
    alunos.append(aluno)
    salvar_dados()
    return {"mensagem": "Aluno adicionado com sucesso!"}

@app.get("/notas_aluno/{aluno_id}")
async def recuperar_notas_aluno(aluno_id: int):
    for aluno in alunos:
        if aluno["id"] == aluno_id:
            return aluno
    raise HTTPException(status_code=404, detail="Aluno não encontrado!")

@app.get("/notas_disciplina/{disciplina}")
async def recuperar_notas_disciplina(disciplina: str):
    notas_disciplina = []
    for aluno in alunos:
        if disciplina in aluno["notas"]:
            notas_disciplina.append({"nome": aluno["nome"], "nota": aluno["notas"][disciplina]})

    notas_ordenadas = notas_disciplina.sort(key=lambda x: x["nota"])
    return notas_ordenadas

def calcular_media(notas):
    return sum(notas) / len(notas)

def calcular_mediana(notas):
    notas_ordenadas = sorted(notas)
    n = len(notas)
    mid = n // 2
    if n % 2 == 0:
        return (notas_ordenadas[mid - 1] + notas_ordenadas[mid]) / 2
    else:
        return notas_ordenadas[mid]

def calcular_desvio_padrao(notas):
    media = calcular_media(notas)
    variancia = sum((nota - media) ** 2 for nota in notas) / len(notas)
    return variancia ** 0.5  

@app.get("/estatisticas_disciplina/{disciplina}")
async def estatisticas_disciplina(disciplina: str):
    notas_disciplina = [aluno["notas"][disciplina] for aluno in alunos if disciplina in aluno["notas"]]
    if not notas_disciplina:
        raise HTTPException(status_code=404, detail="Nenhuma nota encontrada para esta disciplina!")
    
    media = calcular_media(notas_disciplina)
    mediana = calcular_mediana(notas_disciplina)
    desvio_padrao = calcular_desvio_padrao(notas_disciplina)
    return {
        "media": round(media, 1),
        "mediana": round(mediana, 1),
        "desvio_padrao": round(desvio_padrao, 2)
    }

@app.get("/alunos_desempenho_abaixo")
async def alunos_desempenho_abaixo():
    alunos_abaixo = []
    for aluno in alunos:
        for nota in aluno["notas"].values():
            if nota < 6.0:
                alunos_abaixo.append(aluno)
                break
    return alunos_abaixo

@app.delete("/remover_alunos_sem_notas")
async def remover_alunos_sem_notas():
    global alunos
    alunos_com_notas = [aluno for aluno in alunos if aluno["notas"]]
    removidos = len(alunos) - len(alunos_com_notas)
    alunos = alunos_com_notas
    salvar_dados()
    return {"mensagem": f"{removidos} alunos removidos!"}

carregar_dados()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
