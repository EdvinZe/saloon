import { SERVICES } from '../../../shared/data/mockData'

export default function Services() {
  return (
    <section style={{ padding: '80px 48px', borderBottom: '1px solid #2a2218', background: '#0a0a08' }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <p style={{ fontSize: '10px', letterSpacing: '5px', color: '#c9a84c', textTransform: 'uppercase', fontFamily: 'sans-serif', marginBottom: '16px' }}>
          What we offer
        </p>
        <h2 style={{ fontSize: '34px', color: '#e8e0d0', fontWeight: 400 }}>Our services</h2>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1px', background: '#2a2218' }}>
        {SERVICES.map(svc => (
          <div key={svc.name} style={{ background: '#0a0a08', padding: '40px 32px' }}>
            <div style={{ width: '32px', height: '1px', background: '#c9a84c', marginBottom: '28px' }} />
            <div style={{ fontSize: '20px', color: '#e8e0d0', marginBottom: '12px' }}>{svc.name}</div>
            <div style={{ fontSize: '13px', color: '#5a5040', fontFamily: 'sans-serif', lineHeight: 1.8, marginBottom: '28px' }}>{svc.desc}</div>
            <div style={{ fontSize: '24px', color: '#c9a84c', fontFamily: 'sans-serif' }}>{svc.price}</div>
            <div style={{ fontSize: '10px', color: '#3a3020', fontFamily: 'sans-serif', letterSpacing: '2px', textTransform: 'uppercase', marginTop: '4px' }}>{svc.dur}</div>
          </div>
        ))}
      </div>
    </section>
  )
}
