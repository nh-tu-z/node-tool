import { ObjectId, Date } from 'mongoose';

export interface IGroup {
    groupId : ObjectId,
    groupName : String,
    description : String,
    state : Number,
    createdAt: Date,
    updatedAt : Date
}

export interface IDevice {
    deviceId : ObjectId,
    groupId : ObjectId,
    deviceName : String,
    description : String,
    state : Number,
    createdAt: Date,
    updatedAt : Date
}

interface IDeviceStatus {
    DeviceId : ObjectId,
    Status : Number,
    CreatedAt : Date,
    UpdatedAt : Date
}

export interface ITag {
    deviceId : ObjectId,
    tagName : String,
    dataType : String,
    scale : String,
    description : String,
    createdAt : Date,
    updatedAt : Date,
    rW : Number
}

export interface IRawData {
    deviceId : ObjectId,
    tagId : ObjectId,
    tagName : String,
    value : String,
    unixTimeStamp : Number,
    timeStamp : Date,
    createdAt : Date
}

interface IUAObject {
    UAObjectId : ObjectId,
    BrowseName : String,
    DataType : String,
}

export interface IUAVariable {
    browseName : String,
    componentOf : Number,
    description : String,
    dataType : Number
}