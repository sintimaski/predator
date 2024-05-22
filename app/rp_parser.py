# TODO Refactor


class RedisProtocolParser:
    def __init__(self):
        self.buffer = b""

    def clean_command(self, command):
        command = [x for x in command if x]
        return command

    def strip_buffer(self):
        while True:
            if self.buffer.startswith(b"\r\n"):
                self.buffer = self.buffer[2:]
            else:
                break

    def parse(self, data):
        self.buffer += data
        responses = []
        # print("+++++++", data)

        while len(self.buffer) > 0:
            self.strip_buffer()

            # print("--------", self.buffer)
            # Check if the buffer starts with a valid Redis protocol marker
            if self.buffer.startswith(b"*"):
                # Parse multi-bulk response
                end_of_resp_index = self.buffer.find(b"\r\n")
                # print("+++++++", self.buffer, end_of_resp_index)
                if end_of_resp_index == -1:
                    break  # Incomplete response, wait for more data
                num_elements = int(self.buffer[1:end_of_resp_index])
                self.buffer = self.buffer[end_of_resp_index + 2 :]
                # print("123123", self.buffer)
                response = []
                for _ in range(num_elements):
                    response.append(self._parse_element())
                if response is not None and response[0] != "":
                    responses.append(response)

            elif self.buffer.startswith(b"$"):
                # Parse bulk string response
                end_of_resp_index = self.buffer.find(b"\r\n")
                if end_of_resp_index == -1:
                    break  # Incomplete response, wait for more data
                element_length = int(self.buffer[1:end_of_resp_index])
                if element_length == -1:
                    response = None  # Null response
                else:
                    start_of_data_index = end_of_resp_index + 2
                    end_of_data_index = start_of_data_index + element_length
                    if len(self.buffer) < end_of_data_index + 2:
                        break  # Incomplete response, wait for more data
                    response = self.buffer[start_of_data_index:end_of_data_index]
                    self.buffer = self.buffer[end_of_data_index:]
                # print("+_+_+_+_+_", response, self.buffer)
                if response is not None and response[0] != "":
                    if isinstance(response, bytes):
                        responses.append([response])
                    else:
                        responses.append(response)
            elif self.buffer.startswith(b"+"):
                responses.append([self._parse_simple_string()])
            else:
                raise ValueError(f"Invalid Redis protocol {self.buffer}")

        return responses

    def _parse_element(self):
        self.strip_buffer()
        # print("--------", self.buffer)
        # Parse a single element from the buffer
        if self.buffer.startswith(b"$"):
            return self._parse_bulk_string().decode()
        elif self.buffer.startswith(b":"):
            return self._parse_integer()
        elif self.buffer.startswith(b"+"):
            return self._parse_simple_string()
        elif self.buffer.startswith(b"-"):
            return self._parse_error().decode()
        else:
            raise ValueError(f"Invalid Redis protocol {self.buffer}")

    def _parse_bulk_string(self):
        # Parse a bulk string
        end_of_resp_index = self.buffer.find(b"\r\n")
        if end_of_resp_index == -1:
            raise ValueError("Incomplete bulk string")
        element_length = int(self.buffer[1:end_of_resp_index])
        if element_length == -1:
            result = None  # Null bulk string
        else:
            start_of_data_index = end_of_resp_index + 2
            end_of_data_index = start_of_data_index + element_length
            result = self.buffer[start_of_data_index:end_of_data_index]
        self.buffer = self.buffer[end_of_data_index + 2 :]
        return result

    def _parse_integer(self):
        # Parse an integer
        end_of_resp_index = self.buffer.find(b"\r\n")
        if end_of_resp_index == -1:
            raise ValueError("Incomplete integer")
        result = int(self.buffer[1:end_of_resp_index])
        self.buffer = self.buffer[end_of_resp_index + 2 :]
        return result

    def _parse_simple_string(self):
        # Parse a simple string
        end_of_resp_index = self.buffer.find(b"\r\n")
        if end_of_resp_index == -1:
            raise ValueError("Incomplete simple string")
        result = self.buffer[1:end_of_resp_index].decode()
        self.buffer = self.buffer[end_of_resp_index + 2 :]
        return result

    def _parse_error(self):
        # Parse an error
        end_of_resp_index = self.buffer.find(b"\r\n")
        if end_of_resp_index == -1:
            raise ValueError("Incomplete error")
        error_message = self.buffer[1:end_of_resp_index].decode()
        self.buffer = self.buffer[end_of_resp_index + 2 :]
        raise ValueError(error_message)
