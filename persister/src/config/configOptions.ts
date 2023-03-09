import { ConnectOptions } from "mongoose";

export const dbOptions : ConnectOptions = {
    socketTimeoutMS : 40000,
    keepAlive : true,
    keepAliveInitialDelay: 300000
};