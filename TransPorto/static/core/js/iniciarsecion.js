import React from 'react';

export default function Widget() {
    const mediaUrl = '/media/'; 

    return (
        <div className="min-h-screen bg-cover bg-center flex items-center justify-center" style={{ backgroundImage: 'url(https://placehold.co/1200x800)' }}>
            <div className="absolute top-4 right-4">
                <button className="bg-pink-200 text-black py-2 px-4 rounded-full">INICIAR SESIÓN</button>
            </div>
            <div className="bg-white bg-opacity-90 p-8 rounded-lg shadow-lg max-w-sm w-full">
                <div className="flex items-center mb-6">
                    <img src={`${mediaUrl}logo.jpg`} alt="Transporto Logo" className="mr-4" />
                    <h1 className="text-2xl font-bold text-blue-600">INICIAR SESIÓN</h1>
                </div>
                <form>
                    <div className="mb-4">
                        <label htmlFor="email" className="block text-sm font-medium text-zinc-700">Email</label>
                        <input type="email" id="email" className="mt-1 block w-full p-2 border border-zinc-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
                    </div>
                    <div className="mb-6">
                        <label htmlFor="password" className="block text-sm font-medium text-zinc-700">Contraseña</label>
                        <input type="password" id="password" className="mt-1 block w-full p-2 border border-zinc-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
                    </div>
                    <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700">INICIAR SESIÓN</button>
                </form>
                <div className="mt-4 text-center">
                    <a href="#" className="text-blue-600 hover:underline">Regístrate</a>
                </div>
            </div>
        </div>
    );
}
