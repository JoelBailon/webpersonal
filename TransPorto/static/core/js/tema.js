// static/js/tema.js

document.addEventListener('DOMContentLoaded', () => {
  const body = document.body;
  const titulo = document.getElementById('titulo');
  const subtitulo = document.getElementById('subtitulo');
  const tituloSecundario = document.getElementById('tituloSecundario');
  const contenedorCooperativas = document.getElementById('contenedorCooperativas');

  function applyTheme(theme) {
    if (theme === 'dark') {
      // Fondo oscuro
      body.style.backgroundImage = 'none';
      body.style.backgroundColor = '#130b1f';
      body.style.color = 'white';

      // Títulos y textos
      if (titulo) titulo.style.color = 'white';
      if (subtitulo) subtitulo.style.color = 'white';
      if (tituloSecundario) tituloSecundario.style.color = 'white';

      // Fondo y texto de tarjetas
      if (contenedorCooperativas) {
        // Todos los divs hijos de contenedorCooperativas
        contenedorCooperativas.querySelectorAll('div').forEach(div => {
          div.style.backgroundColor = '#1e1a2a'; // un fondo oscuro para tarjetas
          div.style.color = 'white';
        });
        // Los links dentro de esos divs mantienen texto blanco y el hover azul más oscuro
        contenedorCooperativas.querySelectorAll('a').forEach(a => {
          a.style.color = 'white';
          a.style.backgroundColor = '#3b2f59'; // azul oscuro para botones
          a.onmouseover = () => a.style.backgroundColor = '#2b2242';
          a.onmouseout = () => a.style.backgroundColor = '#3b2f59';
        });
      }

    } else {
      // Modo claro
      body.style.backgroundColor = '';
      body.style.backgroundImage = 'linear-gradient(to right, #bbf7d0, #bfdbfe)';
      body.style.color = 'black';

      if (titulo) titulo.style.color = 'black';
      if (subtitulo) subtitulo.style.color = '#1e3a8a'; // azul oscuro
      if (tituloSecundario) tituloSecundario.style.color = 'black';

      if (contenedorCooperativas) {
        contenedorCooperativas.querySelectorAll('div').forEach(div => {
          div.style.backgroundColor = 'white';
          div.style.color = 'black';
        });
        contenedorCooperativas.querySelectorAll('a').forEach(a => {
          a.style.color = 'white';
          a.style.backgroundColor = '#2563eb'; // azul tailwind 600
          a.onmouseover = () => a.style.backgroundColor = '#1e40af'; // azul tailwind 700
          a.onmouseout = () => a.style.backgroundColor = '#2563eb';
        });
      }
    }
  }

  // Aplica el tema guardado al cargar
  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);
});
