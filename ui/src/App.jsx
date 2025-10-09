import React, { useState } from 'react'
import { Send, Sparkles, Loader2, Info, Check, Scroll, AlertTriangle } from 'lucide-react'

export default function App() {
  const [text, setText] = useState('रामोऽस्ति बलवान्')
  const [resp, setResp] = useState(null)
  const [sel, setSel] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // safe derived values to avoid runtime errors if resp shape is unexpected
  const candidates = resp?.candidates || []
  const current = candidates[sel] || { syllables: [], silver_labels: [] }
  const topChanda = resp?.top_chanda || []
  const originalLine = resp?.line || text

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)

    try {
      const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
      const res = await fetch(`${API_BASE}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text, // user input
          sandhi: true // pass options if needed
        })
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'An unknown error occurred.' }))
        throw new Error(errorData.detail || `API request failed with status ${res.status}`)
      }

      const data = await res.json()
      setResp(data)
      setSel(0)
    } catch (err) {
      console.error('API error:', err)
      setError(err?.message || 'An error occurred while analyzing the verse. Please check your input or try again later.')
      // optional user-visible fallback
      // alert("Something went wrong. Check console for details.");
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 30%, #4c1d95 60%, #581c87 100%)',
        position: 'relative',
        width: '100vw',
        overflowX: 'hidden',
        margin: 0,
        padding: 0,
        fontFamily: "'Noto Sans Devanagari', 'Noto Serif', Georgia, serif"
      }}
    >
      <style>{`
        html, body { margin: 0; padding: 0; overflow-x: hidden; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes float { 0%, 100% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-25px) rotate(5deg); } }
        @keyframes shimmer { 0% { background-position: -1000px 0; } 100% { background-position: 1000px 0; } }
        @keyframes pulse-ring { 0% { transform: scale(0.95); opacity: 1; } 100% { transform: scale(1.3); opacity: 0; } }
        * { box-sizing: border-box; }
      `}</style>

      {/* Animated background symbols */}
      <div style={{ position: 'fixed', inset: 0, opacity: 0.04, pointerEvents: 'none', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: '8%', left: '5%', fontSize: '180px', color: '#fbbf24', animation: 'float 8s ease-in-out infinite' }}>ॐ</div>
        <div style={{ position: 'absolute', top: '15%', right: '8%', fontSize: '150px', color: '#f59e0b', animation: 'float 9s ease-in-out infinite', animationDelay: '1s' }}>श्री</div>
        <div style={{ position: 'absolute', bottom: '12%', left: '12%', fontSize: '160px', color: '#fbbf24', animation: 'float 7s ease-in-out infinite', animationDelay: '2s' }}>॥</div>
        <div style={{ position: 'absolute', bottom: '20%', right: '6%', fontSize: '140px', color: '#f59e0b', animation: 'float 8.5s ease-in-out infinite', animationDelay: '0.5s' }}>ॐ</div>
        <div style={{ position: 'absolute', top: '50%', left: '50%', fontSize: '200px', color: '#d97706', opacity: 0.02, animation: 'float 10s ease-in-out infinite', animationDelay: '1.5s' }}>॥</div>
      </div>

      {/* Top shimmer border */}
      <div style={{
        position: 'fixed', top: 0, left: 0, right: 0, height: '5px',
        background: 'linear-gradient(90deg, #fbbf24 0%, #f59e0b 25%, #d97706 50%, #f59e0b 75%, #fbbf24 100%)',
        backgroundSize: '200% 100%', animation: 'shimmer 4s linear infinite', zIndex: 1000, boxShadow: '0 0 20px rgba(251, 191, 36, 0.5)'
      }} />

      <div style={{ position: 'relative', zIndex: 10, maxWidth: '1300px', width: '100%', margin: '0 auto', padding: '40px 20px', minWidth: 0 }}>
        {/* Header */}
        <header style={{ textAlign: 'center', marginBottom: '50px', marginTop: '20px' }}>
          <div style={{ display: 'inline-block', position: 'relative', marginBottom: '28px' }}>
            <div style={{
              position: 'absolute', inset: '-15px',
              background: 'radial-gradient(circle, rgba(251,191,36,0.4) 0%, transparent 70%)',
              borderRadius: '50%', animation: 'pulse-ring 2s ease-out infinite'
            }} />
            <div style={{
              background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%)',
              padding: '26px', borderRadius: '50%', boxShadow: '0 0 80px rgba(251,191,36,0.6), inset 0 0 30px rgba(255,255,255,0.3)',
              width: '110px', height: '110px', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', border: '4px solid rgba(255,255,255,0.4)'
            }}>
              <Scroll style={{ width: '60px', height: '60px', color: 'white', filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.4))' }} />
            </div>
          </div>

          <div style={{ background: 'linear-gradient(90deg, transparent 0%, rgba(251,191,36,0.15) 50%, transparent 100%)', padding: '35px 25px', borderRadius: '25px', marginBottom: '20px', backdropFilter: 'blur(10px)' }}>
            <h1 style={{
              fontSize: 'clamp(44px, 7vw, 72px)', fontWeight: '900',
              background: 'linear-gradient(135deg, #fbbf24 0%, #fde047 30%, #fbbf24 60%, #f59e0b 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
              marginBottom: '16px', lineHeight: '1.1', textShadow: '0 0 60px rgba(251,191,36,0.5)', letterSpacing: '0.03em'
            }}>
              छन्दः शास्त्रम्
            </h1>

            <div style={{ height: '4px', width: '220px', margin: '24px auto', background: 'linear-gradient(90deg, transparent, #fbbf24, #f59e0b, #fbbf24, transparent)', borderRadius: '3px', boxShadow: '0 0 20px rgba(251,191,36,0.5)' }} />

            <h2 style={{
              fontSize: 'clamp(26px, 4.5vw, 40px)', fontWeight: '700', color: '#fde047',
              marginBottom: '18px', letterSpacing: '0.08em', textTransform: 'uppercase', fontFamily: "'Georgia', serif"
            }}>
              Chandas Identifier
            </h2>

            <p style={{
              color: '#e0e7ff', fontSize: 'clamp(15px, 2.2vw, 19px)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '14px', flexWrap: 'wrap', padding: '0 20px', maxWidth: '650px', margin: '0 auto', lineHeight: '1.6'
            }}>
              <Sparkles style={{ width: '22px', height: '22px', color: '#fbbf24' }} />
              Unveil the sacred rhythms of ancient Sanskrit verse
              <Sparkles style={{ width: '22px', height: '22px', color: '#fbbf24' }} />
            </p>
          </div>
        </header>

        {/* Info Card */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(251,191,36,0.12) 0%, rgba(217,119,6,0.12) 100%)', backdropFilter: 'blur(20px)',
          borderRadius: '22px', boxShadow: '0 10px 40px rgba(0,0,0,0.4), inset 0 0 0 1px rgba(251,191,36,0.25)', padding: 'clamp(22px,3.5vw,30px)', marginBottom: '45px', border: '2px solid rgba(251,191,36,0.3)'
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '18px' }}>
            <div style={{ background: 'linear-gradient(135deg,#fbbf24,#f59e0b)', borderRadius: '14px', padding: '14px', flexShrink: 0, boxShadow: '0 4px 15px rgba(251,191,36,0.4)' }}>
              <Info style={{ width: '26px', height: '26px', color: 'white' }} />
            </div>
            <div style={{ color: '#e0e7ff', flex: 1 }}>
              <p style={{ fontWeight: '800', color: '#fde047', marginBottom: '14px', fontSize: 'clamp(16px,2.2vw,20px)', letterSpacing: '0.08em' }}>विधि (Instructions)</p>
              <p style={{ fontSize: 'clamp(14px,2vw,16px)', lineHeight: '1.75', color: '#e0e7ff' }}>
                Enter your Sanskrit verse in Devanagari script. Our analyzer employs classical chandas-śāstra principles
                to identify meter patterns, revealing the गुरु-लघु (heavy-light) prosodic structure.
              </p>
            </div>
          </div>
        </div>

        {/* Error box */}
        {error && (
          <div style={{
            background: 'linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(220,38,38,0.15) 100%)',
            backdropFilter: 'blur(15px)', borderRadius: '22px', boxShadow: '0 10px 40px rgba(0,0,0,0.4), inset 0 0 0 1px rgba(239,68,68,0.3)',
            padding: 'clamp(22px,3.5vw,30px)', marginBottom: '45px', border: '2px solid rgba(239,68,68,0.4)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
              <div style={{ background: 'linear-gradient(135deg,#ef4444,#dc2626)', borderRadius: '14px', padding: '14px', boxShadow: '0 4px 15px rgba(239,68,68,0.4)' }}>
                <AlertTriangle style={{ width: '26px', height: '26px', color: 'white' }} />
              </div>
              <p style={{ color: '#fca5a5', fontSize: 'clamp(14px,2vw,16px)', lineHeight: '1.75', fontWeight: '600', margin: 0 }}>{error}</p>
            </div>
          </div>
        )}

        {/* Input section */}
        <div style={{ marginBottom: '45px', width: '100%' }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(251,191,36,0.08) 0%, rgba(217,119,6,0.08) 100%)', backdropFilter: 'blur(25px)', borderRadius: '28px',
            boxShadow: '0 25px 70px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(251,191,36,0.3)', padding: 'clamp(28px,4.5vw,40px)', border: '2px solid rgba(251,191,36,0.25)', position: 'relative', overflow: 'hidden'
          }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px', background: 'linear-gradient(90deg, transparent, #fbbf24, #f59e0b, #fbbf24, transparent)' }} />

            <label style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '14px', fontSize: 'clamp(19px,2.8vw,24px)', fontWeight: '800', color: '#fde047', marginBottom: '22px' }}>
              <span style={{ fontSize: 'clamp(30px,4.5vw,40px)' }}>📜</span>
              श्लोक प्रविष्टि
              <span style={{ fontSize: 'clamp(14px,2vw,16px)', fontWeight: 'normal', color: '#c4b5fd', marginLeft: '10px' }}>(Sanskrit Verse Input)</span>
            </label>

            <textarea
              rows={4}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="यथा: रामोऽस्ति बलवान् | धर्मो रक्षति रक्षितः..."
              disabled={loading}
              style={{
                width: '100%', padding: 'clamp(20px,3.5vw,28px)', fontSize: 'clamp(22px,3.5vw,34px)', border: '2px solid rgba(251,191,36,0.35)',
                borderRadius: '18px', outline: 'none', resize: 'vertical', color: '#fafafa', caretColor: '#fbbf24',
                fontFamily: "'Noto Sans Devanagari', 'Noto Serif', Georgia, serif", background: 'rgba(30,27,75,0.7)', transition: 'all 0.3s ease', minHeight: '150px', boxShadow: 'inset 0 3px 15px rgba(0,0,0,0.4)', fontWeight: '500'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#fbbf24'
                e.target.style.boxShadow = 'inset 0 3px 15px rgba(0,0,0,0.4), 0 0 20px rgba(251,191,36,0.3)'
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'rgba(251,191,36,0.35)'
                e.target.style.boxShadow = 'inset 0 3px 15px rgba(0,0,0,0.4)'
              }}
            />

            <button
              onClick={handleSubmit}
              disabled={loading || !text.trim()}
              style={{
                marginTop: '26px', width: '100%',
                background: loading || !text.trim() ? 'rgba(113,113,122,0.4)' : 'linear-gradient(135deg,#fbbf24 0%,#f59e0b 50%,#d97706 100%)',
                color: 'white', fontWeight: '800', padding: 'clamp(16px,2.5vw,20px) clamp(28px,4.5vw,40px)', borderRadius: '18px',
                boxShadow: loading || !text.trim() ? 'none' : '0 12px 50px rgba(251,191,36,0.5), inset 0 2px 0 rgba(255,255,255,0.3)', border: 'none', cursor: loading || !text.trim() ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '14px', fontSize: 'clamp(17px,2.2vw,20px)', letterSpacing: '0.08em', textTransform: 'uppercase'
              }}
              onMouseEnter={(e) => {
                if (!loading && text.trim()) {
                  e.currentTarget.style.transform = 'translateY(-3px)'
                  e.currentTarget.style.boxShadow = '0 16px 60px rgba(251,191,36,0.6), inset 0 2px 0 rgba(255,255,255,0.3)'
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = loading || !text.trim() ? 'none' : '0 12px 50px rgba(251,191,36,0.5), inset 0 2px 0 rgba(255,255,255,0.3)'
              }}
            >
              {loading ? (
                <>
                  <Loader2 style={{ width: '26px', height: '26px', animation: 'spin 1s linear infinite' }} />
                  विश्लेषण चलति...
                </>
              ) : (
                <>
                  <Send style={{ width: '26px', height: '26px' }} />
                  Analyze Chandas
                </>
              )}
            </button>

            {loading && (
              <div style={{ marginTop: '24px', padding: '18px', background: 'rgba(30,27,75,0.7)', borderRadius: '18px', border: '1px solid rgba(251,191,36,0.25)', display: 'flex', alignItems: 'center', gap: '14px' }}>
                <Info style={{ width: '22px', height: '22px', color: '#fbbf24', flexShrink: 0 }} />
                <p style={{ margin: 0, color: '#c4b5fd', fontSize: 'clamp(13px,1.8vw,15px)', lineHeight: '1.6' }}>
                  Due to Render's Free Plan, the server gets spun down after 15 mins of inactivity. It might take 50 seconds or more for the first time.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Results (safe rendering using derived values) */}
        {resp && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '35px', width: '100%' }}>
            {/* Original text */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(251,191,36,0.18) 0%, rgba(217,119,6,0.18) 100%)', borderRadius: '24px', padding: 'clamp(28px,4vw,36px)',
              border: '2px solid rgba(251,191,36,0.45)', boxShadow: '0 18px 50px rgba(0,0,0,0.4), inset 0 0 40px rgba(251,191,36,0.12)'
            }}>
              <p style={{ fontSize: 'clamp(12px,1.8vw,14px)', fontWeight: '800', color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '0.2em', marginBottom: '16px', textAlign: 'center' }}>॥ मूल पाठः ॥</p>
              <p style={{ fontSize: 'clamp(26px,4.5vw,44px)', fontWeight: '800', color: '#fde047', wordWrap: 'break-word', lineHeight: '1.5', textAlign: 'center', textShadow: '0 4px 25px rgba(251,191,36,0.4)' }}>
                {originalLine}
              </p>
            </div>

            {/* Candidates */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(251,191,36,0.1) 0%, rgba(217,119,6,0.1) 100%)', borderRadius: '28px', padding: 'clamp(28px,4.5vw,40px)', border: '2px solid rgba(251,191,36,0.25)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '18px', marginBottom: '28px', flexWrap: 'wrap' }}>
                <div style={{ background: 'linear-gradient(135deg,#fbbf24,#f59e0b)', borderRadius: '14px', padding: '12px' }}>
                  <Sparkles style={{ width: 'clamp(26px,4.5vw,32px)', height: 'clamp(26px,4.5vw,32px)', color: 'white' }} />
                </div>
                <h3 style={{ fontSize: 'clamp(22px,3.5vw,28px)', fontWeight: '800', color: '#fde047', margin: 0 }}>विभाग विकल्पाः</h3>
                <span style={{ fontSize: 'clamp(14px,2vw,16px)', color: '#c4b5fd', fontWeight: '600' }}>(Segmentation Options)</span>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '14px' }}>
                {candidates.length === 0 ? (
                  <div style={{ color: '#c4b5fd', fontWeight: 600 }}>No segmentation candidates returned by the API.</div>
                ) : (
                  candidates.map((c, i) => (
                    <button
                      key={i}
                      onClick={() => setSel(i)}
                      style={{
                        padding: 'clamp(13px,2.5vw,16px) clamp(22px,3.5vw,30px)', borderRadius: '16px', fontWeight: '800',
                        fontSize: 'clamp(15px,2.2vw,18px)', transition: 'all 0.3s ease', border: i === sel ? '2px solid #fbbf24' : '2px solid rgba(251,191,36,0.35)',
                        background: i === sel ? 'linear-gradient(135deg,#fbbf24,#f59e0b)' : 'rgba(30,27,75,0.6)', color: i === sel ? 'white' : '#e0e7ff',
                        cursor: 'pointer', boxShadow: i === sel ? '0 10px 30px rgba(251,191,36,0.5)' : '0 4px 15px rgba(0,0,0,0.3)', transform: i === sel ? 'scale(1.05)' : 'scale(1)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', minWidth: 'fit-content', letterSpacing: '0.05em'
                      }}
                      onMouseEnter={(e) => {
                        if (i !== sel) { e.currentTarget.style.transform = 'scale(1.02)'; e.currentTarget.style.borderColor = 'rgba(251,191,36,0.6)'; }
                      }}
                      onMouseLeave={(e) => {
                        if (i !== sel) { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.borderColor = 'rgba(251,191,36,0.35)'; }
                      }}
                    >
                      {i === sel && <Check style={{ display: 'inline', width: '20px', height: '20px', marginRight: '10px' }} />}
                      विकल्प {i + 1}
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Syllable analysis */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(251,191,36,0.1) 0%, rgba(217,119,6,0.1) 100%)', borderRadius: '28px', padding: 'clamp(28px,4.5vw,40px)', border: '2px solid rgba(251,191,36,0.25)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '18px', marginBottom: '32px', flexWrap: 'wrap' }}>
                <div style={{ background: 'linear-gradient(135deg,#fbbf24,#f59e0b)', borderRadius: '14px', padding: '12px' }}>
                  <span style={{ fontSize: 'clamp(26px,4.5vw,36px)' }}>🔤</span>
                </div>
                <h3 style={{ fontSize: 'clamp(22px,3.5vw,28px)', fontWeight: '800', color: '#fde047', margin: 0 }}>अक्षर विश्लेषणम्</h3>
                <span style={{ fontSize: 'clamp(14px,2vw,16px)', color: '#c4b5fd', fontWeight: '600' }}>(Syllable Analysis)</span>
              </div>

              <div style={{ background: 'rgba(30,27,75,0.5)', borderRadius: '22px', padding: 'clamp(24px,3.5vw,32px)', border: '1px solid rgba(251,191,36,0.25)', boxShadow: 'inset 0 3px 15px rgba(0,0,0,0.4)' }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '18px', justifyContent: 'center' }}>
                  {current.syllables.length === 0 ? (
                    <div style={{ color: '#c4b5fd', fontWeight: 600 }}>No syllables available for this candidate.</div>
                  ) : (
                    current.syllables.map((s, i) => {
                      const lab = (current.silver_labels && current.silver_labels[i]) || 'L'
                      const isGuru = lab === 'G'
                      return (
                        <div key={i} style={{
                          position: 'relative', borderRadius: '18px', padding: 'clamp(16px,2.5vw,20px)',
                          boxShadow: isGuru ? '0 10px 25px rgba(239,68,68,0.4), inset 0 0 20px rgba(239,68,68,0.1)' : '0 10px 25px rgba(34,197,94,0.4), inset 0 0 20px rgba(34,197,94,0.1)',
                          border: '2px solid', borderColor: isGuru ? 'rgba(239,68,68,0.6)' : 'rgba(34,197,94,0.6)',
                          background: isGuru ? 'linear-gradient(135deg, rgba(127,29,29,0.5), rgba(153,27,27,0.5))' : 'linear-gradient(135deg, rgba(20,83,45,0.5), rgba(22,101,52,0.5))',
                          transition: 'all 0.3s ease', minWidth: 'fit-content', display: 'inline-block', backdropFilter: 'blur(10px)'
                        }}>
                          <div style={{ fontSize: 'clamp(26px,3.5vw,36px)', fontWeight: '800', color: isGuru ? '#fca5a5' : '#86efac', marginBottom: '8px', wordWrap: 'break-word', textShadow: isGuru ? '0 3px 15px rgba(239,68,68,0.6)' : '0 3px 15px rgba(34,197,94,0.6)' }}>
                            {s}
                          </div>
                          <div style={{ fontSize: 'clamp(11px,1.8vw,13px)', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.1em', color: isGuru ? '#fecaca' : '#bbf7d0', whiteSpace: 'nowrap' }}>
                            {isGuru ? 'गुरु (G)' : 'लघु (L)'}
                          </div>
                          <div style={{
                            position: 'absolute', top: '-12px', right: '-12px', width: 'clamp(28px,3.5vw,32px)', height: 'clamp(28px,3.5vw,32px)', borderRadius: '50%',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 'clamp(13px,1.8vw,15px)', fontWeight: '900', color: 'white',
                            background: isGuru ? 'linear-gradient(135deg,#ef4444,#dc2626)' : 'linear-gradient(135deg,#22c55e,#16a34a)', boxShadow: isGuru ? '0 6px 18px rgba(239,68,68,0.6)' : '0 6px 18px rgba(34,197,94,0.6)', border: '3px solid white'
                          }}>
                            {lab}
                          </div>
                        </div>
                      )
                    })
                  )}
                </div>
              </div>

              {/* Pattern */}
              <div style={{ marginTop: '32px', background: 'rgba(30,27,75,0.7)', borderRadius: '18px', padding: 'clamp(18px,2.5vw,24px)', border: '2px solid rgba(251,191,36,0.35)', boxShadow: 'inset 0 3px 15px rgba(0,0,0,0.4)' }}>
                <p style={{ fontSize: 'clamp(12px,1.8vw,14px)', fontWeight: '800', color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '0.2em', marginBottom: '14px', textAlign: 'center' }}>गण पद्धति (Pattern)</p>
                <p style={{ fontSize: 'clamp(22px,3.5vw,40px)', fontFamily: 'monospace', letterSpacing: '0.2em', textAlign: 'center', color: '#fde047', margin: 0, fontWeight: '800' }}>
                  {current.silver_labels && current.silver_labels.length ? current.silver_labels.map(l => l || 'L').join(' ') : '—'}
                </p>
              </div>
            </div>

            {/* Top chandas */}
            <div style={{ background: 'linear-gradient(135deg, rgba(251,191,36,0.12) 0%, rgba(217,119,6,0.12) 100%)', borderRadius: '28px', padding: 'clamp(28px,4.5vw,40px)', border: '2px solid rgba(251,191,36,0.25)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '18px', marginBottom: '32px', flexWrap: 'wrap' }}>
                <div style={{ background: 'linear-gradient(135deg,#fbbf24,#f59e0b)', borderRadius: '14px', padding: '12px' }}>
                  <span style={{ fontSize: 'clamp(26px,4.5vw,36px)' }}>🏆</span>
                </div>
                <h3 style={{ fontSize: 'clamp(22px,3.5vw,28px)', fontWeight: '800', color: '#fde047', margin: 0 }}>छन्दः मेलनम्</h3>
                <span style={{ fontSize: 'clamp(14px,2vw,16px)', color: '#c4b5fd', fontWeight: '600' }}>(Meter Matches)</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
                {topChanda.length === 0 ? (
                  <div style={{ color: '#c4b5fd', fontWeight: 600 }}>No meter matches returned by the API.</div>
                ) : (
                  topChanda.map((c, idx) => {
                    const isTop = idx === 0
                    const medals = ['🥇', '🥈', '🥉']
                    return (
                      <div key={c.meter || idx} style={{
                        borderRadius: '20px', padding: 'clamp(22px,3.5vw,28px)', transition: 'all 0.3s ease',
                        border: '2px solid', borderColor: isTop ? '#fbbf24' : 'rgba(251,191,36,0.35)',
                        background: isTop ? 'linear-gradient(135deg, rgba(251,191,36,0.22), rgba(217,119,6,0.22))' : 'rgba(30,27,75,0.5)',
                        boxShadow: isTop ? '0 15px 40px rgba(251,191,36,0.4)' : '0 6px 20px rgba(0,0,0,0.3)'
                      }}>
                        {isTop && <><div style={{ position: 'absolute', left: 0, right: 0, top: 0, height: '3px', background: 'linear-gradient(90deg, transparent, #fbbf24, #f59e0b, #fbbf24, transparent)' }} /><div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: '3px', background: 'linear-gradient(90deg, transparent, #fbbf24, #f59e0b, #fbbf24, transparent)' }} /></>}
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '24px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '24px', flex: 1, minWidth: '220px' }}>
                            <div style={{
                              fontSize: 'clamp(22px,3.5vw,32px)', fontWeight: '900', borderRadius: '50%', width: 'clamp(56px,7vw,68px)', height: 'clamp(56px,7vw,68px)',
                              display: 'flex', alignItems: 'center', justifyContent: 'center', background: isTop ? 'linear-gradient(135deg,#fbbf24,#f59e0b)' : 'rgba(251,191,36,0.25)',
                              color: isTop ? 'white' : '#fbbf24'
                            }}>{idx < 3 ? medals[idx] : idx + 1}</div>
                            <div style={{ flex: 1, minWidth: 0 }}>
                              <p style={{ fontSize: 'clamp(24px,4.5vw,36px)', fontWeight: '900', color: isTop ? '#fde047' : '#e0e7ff', margin: 0 }}>{c.meter || 'Unknown meter'}</p>
                            </div>
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <p style={{ fontSize: 'clamp(11px,1.8vw,13px)', fontWeight: '800', color: '#fbbf24', textTransform: 'uppercase', marginBottom: '8px' }}>सङ्ख्या</p>
                            <p style={{ fontSize: 'clamp(32px,4.5vw,46px)', fontWeight: '900', color: isTop ? '#fde047' : '#c4b5fd', margin: 0 }}>{(typeof c.score === 'number' ? c.score.toFixed(2) : (c.score || '—'))}</p>
                          </div>
                        </div>

                        {isTop && (
                          <div style={{ marginTop: '18px', paddingTop: '18px', borderTop: '2px solid rgba(251,191,36,0.4)' }}>
                            <p style={{ fontSize: 'clamp(14px,2.2vw,17px)', color: '#fde047', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '12px', margin: 0 }}>
                              <Check style={{ width: '20px', height: '20px' }} /> उत्तम मेलनम् | Best Match for this Segmentation
                            </p>
                          </div>
                        )}
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer style={{ marginTop: '70px', textAlign: 'center', paddingBottom: '50px' }}>
          <div style={{ display: 'inline-block', padding: 'clamp(16px,2.5vw,20px) clamp(28px,4.5vw,36px)', background: 'linear-gradient(135deg, rgba(251,191,36,0.12), rgba(217,119,6,0.12))', borderRadius: '9999px', boxShadow: '0 10px 30px rgba(0,0,0,0.4)', border: '2px solid rgba(251,191,36,0.3)' }}>
            <p style={{ fontSize: 'clamp(14px,2vw,17px)', margin: 0, color: '#e0e7ff', letterSpacing: '0.04em', lineHeight: '1.6', fontWeight: '600' }}>
              <span style={{ color: '#fbbf24', fontWeight: '800' }}>॥</span> प्राचीन काव्यशास्त्रस्य संरक्षणम् <span style={{ color: '#fbbf24', fontWeight: '800' }}>॥</span>
              <br />
              <span style={{ fontSize: 'clamp(12px,1.8vw,14px)', color: '#c4b5fd', marginTop: '6px', display: 'inline-block' }}>Preserving the sacred science of Sanskrit prosody</span>
            </p>
          </div>

          <div style={{ marginTop: '30px', display: 'flex', justifyContent: 'center', gap: '20px', flexWrap: 'wrap' }}>
            <div style={{ fontSize: 'clamp(36px,5vw,48px)', opacity: 0.5, animation: 'float 4s ease-in-out infinite', color: '#fbbf24' }}>ॐ</div>
            <div style={{ fontSize: 'clamp(36px,5vw,48px)', opacity: 0.5, animation: 'float 4s ease-in-out infinite', animationDelay: '0.7s', color: '#f59e0b' }}>॥</div>
            <div style={{ fontSize: 'clamp(36px,5vw,48px)', opacity: 0.5, animation: 'float 4s ease-in-out infinite', animationDelay: '1.4s', color: '#fbbf24' }}>श्री</div>
          </div>
        </footer>
      </div>

      {/* Bottom shimmer border */}
      <div style={{
        position: 'fixed', bottom: 0, left: 0, right: 0, height: '5px',
        background: 'linear-gradient(90deg, #fbbf24 0%, #f59e0b 25%, #d97706 50%, #f59e0b 75%, #fbbf24 100%)',
        backgroundSize: '200% 100%', animation: 'shimmer 4s linear infinite', zIndex: 1000, boxShadow: '0 0 20px rgba(251,191,36,0.5)'
      }} />
    </div>
  )
}
