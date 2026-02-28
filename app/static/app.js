const API_BASE = '/api'

async function getMenu(){
  const res = await fetch(`${API_BASE}/menu`)
  return res.json()
}

function el(sel){return document.querySelector(sel)}

function addMessage(text, cls){
  const m = document.createElement('div')
  m.className = 'msg ' + cls
  m.textContent = text
  el('#messages').appendChild(m)
}

function setLoading(on){
  el('#loading').classList.toggle('hidden', !on)
}

async function init(){
  const menu = await getMenu()
  const container = el('#options')
  container.innerHTML = ''
  menu.menu.forEach(opt=>{
    const btn = document.createElement('button')
    btn.textContent = opt
    btn.onclick = async ()=>{
      if(opt === 'Ask a Question'){
        addMessage('Please type your question and press Ask.', 'bot')
        return
      }
      setLoading(true)
      const res = await fetch(`${API_BASE}/chat`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'guided', option:opt})})
      const j = await res.json()
      addMessage(opt + ': ' + (j.answer || JSON.stringify(j)), 'bot')
      setLoading(false)
    }
    container.appendChild(btn)
  })
}

el('#ask').onclick = async () =>{
  const q = el('#question').value
  if(!q) return
  addMessage(q, 'user')
  setLoading(true)
  const res = await fetch(`${API_BASE}/chat`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'ask', question:q})})
  const j = await res.json()
  if(j && j.answer) addMessage(j.answer + `\n(confidence: ${j.confidence})`, 'bot')
  else addMessage('No answer received.', 'bot')
  setLoading(false)
}

el('#main-menu').onclick = ()=>{
  init()
}

init()
