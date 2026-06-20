import { useEffect, useState } from "react";

const services = [
  {
    name: "FastAPI",
    description: "Simulation, metrics, checkpoint, and explanation API",
    url: "http://localhost:8000/docs"
  },
  {
    name: "PostgreSQL",
    description: "Structured storage for runs, events, metrics, and models",
    url: null
  },
  {
    name: "Redis",
    description: "Cache and lightweight coordination layer",
    url: null
  },
  {
    name: "MinIO",
    description: "Object storage for models and checkpoints",
    url: "http://localhost:9001"
  },
  {
    name: "Prometheus",
    description: "Metrics collection",
    url: "http://localhost:9090"
  },
  {
    name: "Grafana",
    description: "Monitoring dashboards",
    url: "http://localhost:3001"
  },
  {
    name: "TensorBoard",
    description: "Training visualization",
    url: "http://localhost:6006"
  },
  {
    name: "Nginx",
    description: "Reverse proxy for dashboard and API",
    url: "http://localhost:8080"
  }
];

function App() {
  const [apiHealth, setApiHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/health")
      .then((response) => {
        if (!response.ok) {
          throw new Error("API health check failed");
        }
        return response.json();
      })
      .then((data) => {
        setApiHealth(data);
        setError(null);
      })
      .catch((err) => {
        setError(err.message);
      });
  }, []);

  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">Dockerized Development Foundation</p>
        <h1>Warehouse AI Simulator</h1>
        <p className="subtitle">
          A production-oriented simulation, reinforcement learning, monitoring,
          and LLM explanation platform for autonomous warehouse robots.
        </p>
      </section>

      <section className="status-panel">
        <div>
          <h2>API Status</h2>
          {apiHealth ? (
            <pre>{JSON.stringify(apiHealth, null, 2)}</pre>
          ) : (
            <p className="error">
              {error ? error : "Checking API health..."}
            </p>
          )}
        </div>
      </section>

      <section className="grid">
        {services.map((service) => (
          <article className="card" key={service.name}>
            <h3>{service.name}</h3>
            <p>{service.description}</p>
            {service.url ? (
              <a href={service.url} target="_blank" rel="noreferrer">
                Open service
              </a>
            ) : (
              <span className="muted">Internal service</span>
            )}
          </article>
        ))}
      </section>
    </main>
  );
}

export default App;
