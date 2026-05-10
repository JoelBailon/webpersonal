import React from 'react';

export default function Widget() {
    const mediaUrl = '/media/'; // URL base para archivos de medios

    return (
        <div className="min-h-screen bg-gradient-to-r from-green-200 to-blue-200 p-4">
            <div className="flex justify-between items-center mb-4">
                <div className="flex items-center space-x-2">
                    <div className="text-4xl font-bold">TRANSPORTO</div>
                    <div className="italic">La forma inteligente de moverse</div>
                </div>
                <div className="flex items-center space-x-2">
                    <img src={`${mediaUrl}logo.jpg`} alt="icon" className="w-10 h-10" />
                    <div className="bg-purple-300 text-black px-4 py-2 rounded-full">Saldo</div>
                </div>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-lg flex justify-between items-center">
                <div className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500">SALDO ACTUAL</div>
                <div className="flex items-center space-x-4">
                    <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500">$0,00</div>
                    <button className="bg-pink-200 text-black font-bold px-6 py-2 rounded-full">RECARGAR</button>
                </div>
            </div>
        </div>
    );
}
