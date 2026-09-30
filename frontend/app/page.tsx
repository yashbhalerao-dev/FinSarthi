import Link from "next/link";

export default function HomePage() {
  return (
    <main className="shell">
      <p className="eyebrow">Team NeuroSquad · 50% prototype</p>
      <h1>FinSarthi</h1>
      <p className="lede">
        Financial Policy Discovery, Eligibility &amp; Application Assistant for
        individuals and small businesses. Provide a profile and supporting
        documents. FinSarthi retrieves synthetic demo policies, evaluates
        explicit conditions with a Python rule engine, and shows source-backed
        results. The language model does not decide eligibility.
      </p>
      <div className="actions">
        <Link className="button" href="/dashboard">
          Start
        </Link>
        <Link className="button secondary" href="/profile">
          Create a profile
        </Link>
      </div>
      <div className="grid">
        <section className="card">
          <h2>The problem</h2>
          <p>
            Financial assistance information is scattered, eligibility rules are
            hard to check by hand, and unsupported AI answers are not trustworthy.
          </p>
        </section>
        <section className="card">
          <h2>The approach</h2>
          <p>
            Retrieval finds policy evidence. Python rules return ELIGIBLE,
            NOT_ELIGIBLE, or NEEDS_VERIFICATION. Benefits appear only when the
            source supports them.
          </p>
        </section>
        <section className="card">
          <h2>This demo</h2>
          <p>
            Uses a controlled synthetic corpus. It is decision support, not an
            official government determination.
          </p>
        </section>
      </div>
    </main>
  );
}
