import React from 'react';

export default function Widget() {
    const mediaUrl = '/media/'; // Ajusta la URL base para archivos de medios si es necesario

    return (
        <div className="bg-gradient-to-r from-green-200 to-blue-200 p-4">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-4xl font-bold">TRANSPORTO</h1>
                    <p className="italic">La forma inteligente de moverse</p>
                </div>
                <img src={`${mediaUrl}bus.png`} alt="bus" className="w-48 h-auto" />
            </div>
            <div className="flex justify-around">
                <div className="text-center">
                    <div className="bg-purple-300 rounded-full px-4 py-2 mb-2">
                        <span className="text-xl font-semibold">Saldo</span>
                    </div>
                    <img src={`${mediaUrl}balance-icon.png`} alt="balance icon" className="w-24 h-24 mx-auto" />
                </div>
                <div className="text-center">
                    <div className="bg-purple-300 rounded-full px-4 py-2 mb-2">
                        <span className="text-xl font-semibold">Tarjeta</span>
                    </div>
                    <img src={`${mediaUrl}card-icon.png`} alt="card icon" className="w-24 h-24 mx-auto" />
                </div>
                <div className="text-center">
                    <div className="bg-purple-300 rounded-full px-4 py-2 mb-2">
                        <span className="text-xl font-semibold">Perfil</span>
                    </div>
                    <img src={`${mediaUrl}profile-icon.png`} alt="profile icon" className="w-24 h-24 mx-auto" />
                </div>
            </div>
        </div>
    );
}
