/**
 * Compression utilities for handling large messages
 * Uses pako for gzip compression and browser's native base64 encoding
 */

import * as pako from 'pako';

/**
 * Error class for compression-related errors
 */
export class CompressionError extends Error {
    constructor(message: string, public readonly operation: string) {
        super(message);
        this.name = 'CompressionError';
    }
}

/**
 * Convert Uint8Array to string in a stack-safe way by processing in chunks
 * This avoids "Maximum call stack size exceeded" errors with large arrays
 * @param bytes The Uint8Array to convert
 * @returns String representation of the bytes
 */
function uint8ArrayToString(bytes: Uint8Array): string {
    const CHUNK_SIZE = 8192; // Process in 8KB chunks to avoid stack overflow
    let result = '';

    for (let i = 0; i < bytes.length; i += CHUNK_SIZE) {
        const chunk = bytes.slice(i, i + CHUNK_SIZE);
        result += String.fromCharCode(...chunk);
    }

    return result;
}

/**
 * Compress a string using gzip and encode as base64
 * @param input The string to compress
 * @returns Base64-encoded compressed string
 * @throws CompressionError if compression fails
 */
export function compressString(input: string): string {
    try {
        // Convert string to UTF-8 bytes
        const utf8Bytes = new TextEncoder().encode(input);

        // Compress using gzip
        const compressed = pako.gzip(utf8Bytes);

        // Convert to base64 using stack-safe method
        const base64 = btoa(uint8ArrayToString(compressed));

        return base64;
    } catch (error) {
        throw new CompressionError(
            `Failed to compress string: ${error instanceof Error ? error.message : 'Unknown error'}`,
            'compress'
        );
    }
}

/**
 * Encode a string as base64
 * @param input The string to encode
 * @returns Base64-encoded string
 * @throws CompressionError if encoding fails
 */
export function encodeBase64(input: string): string {
    try {
        // Handle UTF-8 properly by first encoding to bytes then to base64
        const utf8Bytes = new TextEncoder().encode(input);
        const base64 = btoa(uint8ArrayToString(utf8Bytes));

        return base64;
    } catch (error) {
        throw new CompressionError(
            `Failed to encode string as base64: ${error instanceof Error ? error.message : 'Unknown error'}`,
            'encode'
        );
    }
}

/**
 * Decompress a base64-encoded gzip string
 * @param input Base64-encoded compressed string
 * @returns Decompressed original string
 * @throws CompressionError if decompression fails
 */
export function decompressString(input: string): string {
    try {
        // Decode from base64
        const binaryString = atob(input);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        // Decompress using gzip
        const decompressed = pako.ungzip(bytes);

        // Convert back to string
        const result = new TextDecoder().decode(decompressed);

        return result;
    } catch (error) {
        throw new CompressionError(
            `Failed to decompress string: ${error instanceof Error ? error.message : 'Unknown error'}`,
            'decompress'
        );
    }
}

/**
 * Decode a base64-encoded string
 * @param input Base64-encoded string
 * @returns Decoded original string
 * @throws CompressionError if decoding fails
 */
export function decodeBase64(input: string): string {
    try {
        // Decode from base64
        const binaryString = atob(input);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        // Convert back to string
        const result = new TextDecoder().decode(bytes);

        return result;
    } catch (error) {
        throw new CompressionError(
            `Failed to decode base64 string: ${error instanceof Error ? error.message : 'Unknown error'}`,
            'decode'
        );
    }
}

/**
 * Calculate compression ratio for a given string
 * @param original The original string
 * @param compressed The compressed base64 string
 * @returns Compression ratio as a percentage (0-100)
 */
export function getCompressionRatio(original: string, compressed: string): number {
    const originalSize = new TextEncoder().encode(original).length;
    const compressedSize = new TextEncoder().encode(compressed).length;

    if (originalSize === 0) {
        return 0;
    }

    return Math.round((1 - compressedSize / originalSize) * 100);
}

/**
 * Utility function to determine if compression would be beneficial
 * @param input The string to potentially compress
 * @param threshold Minimum size in bytes to consider compression (default: 1024)
 * @returns True if compression is recommended
 */
export function shouldCompress(input: string, threshold: number = 1024): boolean {
    const size = new TextEncoder().encode(input).length;
    return size >= threshold;
}

/**
 * Compress string only if it would be beneficial
 * @param input The string to potentially compress
 * @param threshold Minimum size in bytes to consider compression (default: 1024)
 * @returns Object with compressed data and metadata
 */
export function smartCompress(input: string, threshold: number = 1024): {
    data: string;
    compressed: boolean;
    originalSize: number;
    finalSize: number;
    ratio?: number;
} {
    const originalSize = new TextEncoder().encode(input).length;

    if (!shouldCompress(input, threshold)) {
        return {
            data: input,
            compressed: false,
            originalSize,
            finalSize: originalSize
        };
    }

    try {
        const compressed = compressString(input);
        const finalSize = new TextEncoder().encode(compressed).length;
        const ratio = getCompressionRatio(input, compressed);

        // Only use compression if it actually reduces size significantly
        if (finalSize < originalSize * 0.9) {
            return {
                data: compressed,
                compressed: true,
                originalSize,
                finalSize,
                ratio
            };
        } else {
            // Compression didn't help much, return original
            return {
                data: input,
                compressed: false,
                originalSize,
                finalSize: originalSize
            };
        }
    } catch (error) {
        // If compression fails, return original
        return {
            data: input,
            compressed: false,
            originalSize,
            finalSize: originalSize
        };
    }
}
