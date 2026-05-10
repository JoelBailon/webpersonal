import React from 'react';

export default function Widget() {
    return (
        <div className="bg-gradient-to-r from-green-200 via-blue-200 to-purple-200 min-h-screen p-4">
            <div className="flex justify-between items-center">
                <div className="flex items-center space-x-2">
                    <div className="text-4xl font-bold">TRANSPORTO</div>
                    <img src="/media/card-icon.png" alt="Card Icon" className="w-10 h-10"/>
                </div>
                <div className="text-2xl font-semibold bg-purple-200 px-4 py-2 rounded-full">Tarjeta</div>
            </div>
            <div className="text-lg italic mt-2">La forma inteligente de moverse</div>
            <div className="flex justify-around mt-10">
                <div className="text-center">
                    <div className="bg-gradient-to-r from-pink-200 to-purple-200 px-4 py-2 rounded-lg text-2xl font-semibold mb-4">Solicitar</div>
                    <img src="/media/solicitar-icon.png" alt="Solicitar Icon" className="w-24 h-24 mx-auto"/>
                </div>
                <div className="text-center">
                    <div className="bg-gradient-to-r from-pink-200 to-purple-200 px-4 py-2 rounded-lg text-2xl font-semibold mb-4">Bloquear</div>
                    <img src="/media/bloquear-icon.png" alt="Bloquear Icon" className="w-24 h-24 mx-auto"/>
                </div>
            </div>
        </div>
    )
}
