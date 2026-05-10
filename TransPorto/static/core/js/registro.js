import React from 'react';

export default function Widget() {
    const mediaUrl = process.env.PUBLIC_URL + '/media/'; // Adjust the URL as needed

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-green-200 to-blue-200 p-4">
            <div className="flex items-center justify-between w-full max-w-4xl mb-8">
                <div className="flex items-center space-x-4">
                    <img src={`${mediaUrl}logo.png`} alt="Logo" className="w-12 h-12" />
                    <div>
                        <h1 className="text-4xl font-bold">TRANSPORTO</h1>
                        <p className="italic">La forma inteligente de moverse</p>
                    </div>
                </div>
                <img src="https://placehold.co/50x50" alt="Profile Icon" className="w-12 h-12" />
            </div>
            <div className="w-full max-w-md bg-white p-8 rounded-lg shadow-lg">
                <h2 className="text-2xl font-bold text-center bg-purple-300 rounded-full py-2 mb-8">Perfil</h2>
                <form className="space-y-6">
                    <div>
                        <label className="block text-lg font-bold mb-2">NOMBRES</label>
                        <input type="text" className="w-full p-3 rounded-lg bg-zinc-200" placeholder="Nombres" />
                    </div>
                    <div>
                        <label className="block text-lg font-bold mb-2">APELLIDOS</label>
                        <input type="text" className="w-full p-3 rounded-lg bg-zinc-200" placeholder="Apellidos" />
                    </div>
                    <div>
                        <label className="block text-lg font-bold mb-2">CIUDAD</label>
                        <input type="text" className="w-full p-3 rounded-lg bg-zinc-200" placeholder="Ciudad" />
                    </div>
                    <div>
                        <label className="block text-lg font-bold mb-2">CELULAR</label>
                        <input type="text" className="w-full p-3 rounded-lg bg-zinc-200" placeholder="Celular" />
                    </div>
                </form>
            </div>
        </div>
    );
}
