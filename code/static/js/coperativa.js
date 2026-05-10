export default function Widget() {
    return (
      <div className="bg-[#A0E0E0] p-6 min-h-screen">
        <div className="flex items-center justify-between mb-6">
          <img src="https://placehold.co/150x50?text=TRANSPORTO" alt="Transporto Logo" />
          <img undefinedhidden="true" alt="User Icon" src="https://openui.fly.dev/openui/24x24.svg?text=👤" className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold mb-4">Cooperativas</h2>
        <ul className="space-y-4">
          <li className="bg-white p-4 rounded-lg shadow-md">Ciudad del Valle</li>
          <li className="bg-white p-4 rounded-lg shadow-md">Portoviejo</li>
          <li className="bg-white p-4 rounded-lg shadow-md">Picoaza</li>
          <li className="bg-white p-4 rounded-lg shadow-md">Higuero</li>
        </ul>
        <button className="mt-6 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-500">Rutas</button>
      </div>
    )
  }