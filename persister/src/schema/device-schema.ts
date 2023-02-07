import { Schema, model, Types } from 'mongoose';
import { IUAVariable, ITag, IRawData, IGroup, IDevice } from '../interfaces/documents';
import { schemaName, errMsg } from '../const';

// UA Variable
const uaVariableSchema = new Schema<IUAVariable>({
    browseName: { type: String, required: true },
    componentOf: { type: Number, required: true },
    description: { type: String },
    dataType : { type: Number, required: true }
  });
  
const UAVariableModel = model<IUAVariable>(schemaName.uaVariable, uaVariableSchema);

// Tag
const tagSchema = new Schema<ITag>({
  deviceId: { type: Types.ObjectId, required: true},
  tagName: { type: String, required: true },
  dataType: { type: Number, required: true },
  scale: { type: Number, required: true },
  description: { type: String },
  createdAt: { type: Date, required: true },
  updatedAt: { type: Date, required: true },
  rW: { type: Boolean, required: true}
});

const TagModel = model<ITag>(schemaName.tag, tagSchema);

// Raw Data
const rawDataSchema = new Schema<IRawData>({
  deviceId: { type: Types.ObjectId, required: true},
  tagId: { type: Types.ObjectId, required: true},
  tagName: { type: String, required: true },
  value: { type: String, required: true },
  unixTimeStamp: { type: Number, required: true },
  timeStamp: { type: Date, required: true },
  createdAt: { type: Date, required: true }
})

const RawDataModel = model<IRawData>(schemaName.rawData, rawDataSchema);

// Group
const groupSchema = new Schema<IGroup>({
  groupId: { type: Types.ObjectId, required: true},
  groupName: { type: String, required: true },
  description: { type: String },
  state: { type: Number, required: true },
  createdAt: { type: Date, required: true },
  updatedAt: { type: Date, required: true }
});

const GroupModel = model<IGroup>(schemaName.group, groupSchema);

// Device
const deviceSchema = new Schema<IDevice>({
  deviceId: { type: Types.ObjectId, required: true},
  groupId: { type: Types.ObjectId, required: true},
  deviceName: { type: String, required: true },
  description: { type: String },
  state: { type: Number, required: true },
  createdAt: { type: Date, required: true },
  updatedAt: { type: Date, required: true }
});

const DeviceModel = model<IDevice>(schemaName.device, deviceSchema);

export function schemaBuilder(collectionName: string): any {
    if (collectionName === schemaName.rawData) {
        return RawDataModel;
    }
    else if (collectionName === schemaName.device) {
        return DeviceModel;
    }
    else if (collectionName === schemaName.group) {
        return GroupModel;
    }
    else if (collectionName === schemaName.tag) {
        return TagModel;
    }
    else if (collectionName === schemaName.uaVariable) {
        return UAVariableModel;
    }
    else {
        return errMsg.notSupportSchema;
    }
}