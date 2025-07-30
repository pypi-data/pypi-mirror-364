/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

#pragma once

#include <string>
#include <vector>

typedef std::vector<std::string> StdStringVector;
typedef std::vector<long> StdLongVector;
typedef std::vector<double> StdDoubleVector;

#define unique_pointer std::unique_ptr

namespace PyTango
{
enum ExtractAs
{
    ExtractAsNumpy,
    ExtractAsByteArray,
    ExtractAsBytes,
    ExtractAsTuple,
    ExtractAsList,
    ExtractAsString,
    ExtractAsPyTango3,
    ExtractAsNothing
};

enum ImageFormat
{
    RawImage,
    JpegImage
};

enum GreenMode
{
    GreenModeSynchronous,
    GreenModeFutures,
    GreenModeGevent,
    GreenModeAsyncio
};
} // namespace PyTango
