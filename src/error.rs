// ---------
// IMPORTANT! : never pass server errors to client (secret exposure)
// ---------
//
// TODO: Server has all information and cherry pick what client receives.

pub type Result<T> = cor::result::Result<T, Error>;

#[derive(Debug)]
pub enum Error {}

impl core::fmt::Display for Error {
    fn fmt(&self, fmt: &mut core::fmt::Formatter) -> core::result::Result<(), core::fmt::Error> {
        write!(fmt, "{self:?}")
    }
}
impl std::error::Error for Error {}

impl IntoResponse for Error {
    fn into_response(self) -> Response {
        println!("->> {:<12} - {self:?}", "INTO_RES");

        // Create a placeholder for Axum response.
        let mut response = StatusCode::INTERNAL_SERVER_ERROR.into_response();

        // Insert the Error into the response.
        response.extensions_mut().insert(self);

        response
    }
}
