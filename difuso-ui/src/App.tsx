import Header from "./components/Header.tsx";
import './styles/App.scss'
import {type ChangeEvent, useEffect, useState} from "react";

interface ResultAPI {
    IMCValue: number;
    IMCDifuso: Record<string, number>;
    MainDescription: string;
    RiskDescription: string;
    MainRisk: number;
    RiesgoDifuso: Record<string, number>;
    Recomendaciones: string;
}

function App() {
    const [peso, setPeso] = useState("");
    const [altura, setAltura] = useState("");
    const [edad, setEdad] = useState("");
    const [genero, setGenero] = useState("");
    const [resultado, setResultado] = useState<ResultAPI | null>(null);

    const handleAlturaChange = (e: ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        const num = Number(value);
        if (num > 0 && num <= 220 || value === "") {
            setAltura(value);
        }
    }

    const handlePesoChange = (e: ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        const num = Number(value);
        if (num > 0 && num <= 400 || value === "" ) {
            setPeso(value);
        }
    }

    const handleEdadChange = (e: ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        const num = Number(value);
        if (num > 0 && num <= 110 || value === "") {
            setEdad(value);
        }
    }

    useEffect(() => {
        console.log("Iniciando API");
        if (peso && altura && edad && genero) {
            (async () => {
                const datos = {peso, altura, edad, genero};
                console.log(datos);
                const respuesta = await fetch("http://127.0.0.1:8000/riesgo", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(datos),
                });
                const resultadoAPI: ResultAPI = await respuesta.json();
                console.log(resultadoAPI);
                setResultado(resultadoAPI);
            })();
        }
    }, [peso, altura, edad, genero]);


  return (
    <>
        <Header />
        <main className="App-Main">
            <section className="Card">
                <div className="Card__content">
                    <div className="Left-Box">
                        <div>
                            <label htmlFor="altura">TU ALTURA</label>
                            <div className="field">
                                <input id="altura" type="number" placeholder="Altura" value={altura} onChange={handleAlturaChange} />
                                <span className="unit">cm</span>
                            </div>
                        </div>
                        <div>
                            <label htmlFor="peso">TU PESO</label>
                            <div className="field">
                                <input id="peso" type="number" placeholder="Peso" value={peso} onChange={handlePesoChange} />
                                <span className="unit">kg</span>
                            </div>
                        </div>
                        <div>
                            <label htmlFor="edad">TU EDAD</label>
                            <div className="field">
                                <input
                                    id="edad"
                                    type="number"
                                    placeholder="Edad"
                                    value={edad}
                                    onChange={handleEdadChange}
                                />
                                <span className="unit">años</span>
                            </div>
                        </div>
                        <div>
                            <label htmlFor="genero">TU GÉNERO</label>
                            <div className="field">
                                <select
                                    id="genero"
                                    className="custom-select"
                                    value={genero}
                                    onChange={e => setGenero(e.target.value)}
                                >
                                    <option value="">Selecciona</option>
                                    <option value="masculino">Masculino</option>
                                    <option value="femenino">Femenino</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div className="Divider" aria-hidden="true"></div>

                    <div className="Right-Box">
                        <h2>TU IMC ES</h2>
                        <div className="bmi">{resultado ? `${resultado.IMCValue.toFixed(1)}` : ""}</div>
                        <p className="summary">
                            Clasificación de peso: <strong>{resultado ? resultado?.MainDescription : "Desconocido"}</strong><br/>
                            Riesgo de enfermedad relacionada: <strong>{resultado ? resultado?.RiskDescription : "Desconocido"}</strong><br/>
                            Riesgo en terminos numericos del 1 al 10: <strong>{resultado ? resultado?.MainRisk : "Desconocido"}</strong>
                        </p>
                    </div>
                </div>

                <div className="Bottom-Box">
                    <h2>Tus resultados</h2>
                    <p>
                        {resultado ? `IMC: ${resultado.IMCValue}` : "Ingrese todos los campos para mostrar su IMC y recomendaciones"}
                    </p>
                    <h2>Estados Difusos</h2>
                    <p>
                        {resultado
                            ? `${(resultado.IMCDifuso
                            )}`
                            : ""}
                    </p>
                    <h2>Recomendaciones: </h2>
                    <p>
                        {resultado?.Recomendaciones}
                    </p>
                </div>
            </section>
        </main>
    </>
  )
}

export default App
