import type { NDDataType } from "../types";
export declare function b64encode(data: Uint8Array): string;
export declare function b64decode(data: string): Uint8Array;
export declare function buffer_to_base64(buffer: ArrayBuffer): string;
export declare function base64_to_buffer(base64: string): ArrayBuffer;
export declare function swap(buffer: ArrayBuffer, dtype: NDDataType): void;
//# sourceMappingURL=buffer.d.ts.map